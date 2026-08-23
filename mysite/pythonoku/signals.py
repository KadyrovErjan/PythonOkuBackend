import secrets

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import reset_password_token_created


def generate_reset_code(token):
    """Создаёт короткий код, не совпадающий с другими активными токенами."""
    for _ in range(20):
        code = str(secrets.randbelow(900000) + 100000)
        collision = ResetPasswordToken.objects.filter(key=code).exclude(pk=token.pk).exists()
        if not collision:
            return code
    return str(secrets.randbelow(900000) + 100000)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    code = generate_reset_code(reset_password_token)
    reset_password_token.key = code
    reset_password_token.save(update_fields=['key'])

    username = reset_password_token.user.username
    subject = 'Код восстановления PythonOku'
    text = (
        f'Здравствуйте, {username}!\n\n'
        f'Ваш код восстановления: {code}\n'
        'Он действует 1 час. Если вы не запрашивали сброс пароля, проигнорируйте письмо.'
    )
    html = f"""
    <div style="margin:0;padding:32px 16px;background:#070b14;font-family:Arial,sans-serif;color:#e9edf5">
      <div style="max-width:520px;margin:0 auto;padding:32px;border:1px solid #273149;border-radius:20px;background:#111827">
        <div style="margin-bottom:28px;font-size:22px;font-weight:800">Python<span style="color:#a591ff">Oku</span></div>
        <p style="margin:0 0 8px;color:#a4aec2;font-size:14px">Здравствуйте, {username}!</p>
        <h1 style="margin:0 0 12px;color:#ffffff;font-size:25px">Восстановление пароля</h1>
        <p style="margin:0 0 24px;color:#8793aa;font-size:14px;line-height:1.6">Введите этот код на странице восстановления:</p>
        <div style="padding:18px;border:1px solid #8064ff;border-radius:14px;background:#1c1b38;color:#c3b8ff;font-size:34px;font-weight:800;letter-spacing:12px;text-align:center">{code}</div>
        <p style="margin:24px 0 0;color:#65728a;font-size:12px;line-height:1.6">Код действует 1 час. Никому его не сообщайте. Если вы не запрашивали восстановление, просто проигнорируйте это письмо.</p>
      </div>
    </div>
    """

    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=(
            settings.DEFAULT_FROM_EMAIL
            or settings.EMAIL_HOST_USER
            or 'PythonOku <noreply@localhost>'
        ),
        to=[reset_password_token.user.email],
    )
    message.attach_alternative(html, 'text/html')
    message.send(fail_silently=False)
