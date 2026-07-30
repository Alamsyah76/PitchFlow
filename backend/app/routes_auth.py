"""Auth API — Register, OTP Login, User Profile"""
import os, logging
from fastapi import APIRouter, HTTPException
from app.auth_user import register_user, get_user, generate_otp, verify_otp, verify_user, set_user_tier, get_users, get_tier_for_email
from app.auth import create_jwt_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
async def register(payload: dict):
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    if not name or not email:
        raise HTTPException(400, "Name and email are required")
    if not email or "@" not in email:
        raise HTTPException(400, "Invalid email address")

    ok = register_user(name, email)
    if not ok:
        raise HTTPException(409, "Email already registered. Please login.")

    # Kirim OTP
    code = generate_otp(email)
    _send_otp_email(email, name, code)

    return {"success": True, "message": "Registration successful. Check your email for OTP."}


@router.post("/request-otp")
async def request_otp(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(400, "Email is required")

    user = get_user(email)
    if not user:
        raise HTTPException(404, "Email not registered. Please register first.")

    code = generate_otp(email)
    _send_otp_email(email, user.get("name", "User"), code)
    return {"success": True, "message": "OTP sent to your email."}


@router.post("/verify-otp")
async def verify_otp_endpoint(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    code = (payload.get("code") or "").strip()

    if not email or not code:
        raise HTTPException(400, "Email and code are required")

    valid = verify_otp(email, code)
    if not valid:
        raise HTTPException(400, "Invalid or expired OTP code")

    verify_user(email)
    user = get_user(email)
    token = create_jwt_token(email)
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "email": email,
            "name": user.get("name", "") if user else "",
            "token": token,
        }
    }


@router.post("/logout")
async def logout():
    return {"success": True, "message": "Logged out"}


@router.post("/admin-login")
async def admin_login(payload: dict):
    """Admin login — pake email + password dari .env, tidak perlu OTP"""
    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()
    admin_email = os.environ.get("PITCHFLOW_ADMIN_EMAIL", "").strip().lower()
    admin_pass = os.environ.get("PITCHFLOW_ADMIN_PASSWORD", "")

    if not admin_email or not admin_pass:
        raise HTTPException(500, "Admin not configured. Set PITCHFLOW_ADMIN_EMAIL and PITCHFLOW_ADMIN_PASSWORD in .env")

    if email != admin_email or password != admin_pass:
        raise HTTPException(401, "Invalid admin credentials")

    # Daftarkan / update admin user dengan tier pro
    register_user("Administrator", admin_email)
    set_user_tier(admin_email, "pro")
    verify_user(admin_email)
    token = create_jwt_token(admin_email)

    return {"success": True, "message": "Admin login successful", "data": {"email": admin_email, "name": "Administrator", "role": "admin", "token": token}}


@router.post("/me")
async def me(payload: dict):
    """Get current user info"""
    email = (payload.get("email") or "").strip().lower()
    user = get_user(email)
    if not user:
        raise HTTPException(404, "User not found")
    return {"success": True, "data": {"email": user["email"], "name": user["name"], "tier": user.get("tier", "free"), "verified": user.get("verified", False)}}


@router.post("/users")
async def list_users(payload: dict):
    """List all users (admin only — but for now simple auth check)"""
    email = (payload.get("email") or "").strip().lower()
    admin_email = os.environ.get("PITCHFLOW_ADMIN_EMAIL", "").strip().lower()
    if email != admin_email:
        raise HTTPException(403, "Only admin can list users")
    users = get_users()
    return {"success": True, "data": {e: {"name": u["name"], "tier": u.get("tier", "free"), "verified": u.get("verified", False), "registered_at": u.get("registered_at", "")} for e, u in users.items()}}


@router.post("/set-tier")
async def admin_set_tier(payload: dict):
    """Admin set user tier"""
    admin_email = (payload.get("admin_email") or "").strip().lower()
    target_email = (payload.get("email") or "").strip().lower()
    tier = (payload.get("tier") or "").strip().lower()

    if admin_email != os.environ.get("PITCHFLOW_ADMIN_EMAIL", "").strip().lower():
        raise HTTPException(403, "Only admin can set tier")

    from app.rate_limit import TIERS
    if tier not in TIERS:
        raise HTTPException(400, f"Invalid tier. Choose: {', '.join(TIERS.keys())}")

    user = get_user(target_email)
    if not user:
        raise HTTPException(404, "User not found")

    set_user_tier(target_email, tier)
    return {"success": True, "message": f"{target_email} tier set to {tier}"}


def _send_otp_email(to_email: str, to_name: str, code: str):
    """Kirim OTP via SMTP — panggil dari routes yang sama seperti email campaign"""
    try:
        smtp_host = os.environ.get("SMTP_HOST", "")
        smtp_port = int(os.environ.get("SMTP_PORT", 465))
        smtp_user = os.environ.get("SMTP_USERNAME", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        sender_email = os.environ.get("SENDER_EMAIL", smtp_user)
        sender_name = os.environ.get("SENDER_NAME", "PitchFlow")

        if not smtp_host or not smtp_user or not smtp_pass:
            logger.warning(f"SMTP not configured — OTP for {to_email}: {code}")
            return

        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(f"Halo {to_name},\n\nKode OTP kamu: {code}\n\nKode berlaku 10 menit.\n\n— PitchFlow", "plain", "utf-8")
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = to_email
        msg["Subject"] = f"Kode OTP PitchFlow: {code}"

        with smtplib.SMTP_SSL(smtp_host, smtp_port) as s:
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        logger.info(f"OTP sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send OTP to {to_email}: {e}")
        # Jangan throw — OTP tetap tersimpan, bisa dilihat di log
