from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.conf import settings

from core.models import UserVerification
from django.core.mail import EmailMultiAlternatives

from .tokens import email_verification_token

from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from django.contrib.auth import get_user_model

from apps.api_messages.models import Message

@shared_task(name="mail_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def mail_notifier(user_id, domain, origin='', verification_type=2, subject='', sign_off='', email_to='', cancelled=False, cancelled_reason=""):

    # reason we pass user_id instead of user object
    # kombu.exceptions.EncodeError: Object of type User is not JSON serializable
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return

    try:

        try:
            verifier = UserVerification.objects.get(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False)
            uid = verifier.uid
            token = verifier.token
            verifier.email_address=email_to
        except UserVerification.DoesNotExist:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            UserVerification.objects.filter(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False).update(expired=True, cancelled=cancelled, cancelled_reason="Creating new notification: " + str(cancelled_reason))
            verifier = UserVerification.objects.create(user=user, uid=uid, token=token, origin=origin, verified=False, expired=False, verification_type=verification_type, email_address=email_to)
        except Exception as e:
            verifier = UserVerification.objects.filter(user=user, verified=False, expired=False, verification_type=verification_type, cancelled=False).first()
        
        message = render_to_string('verify_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
            'sign_off': sign_off
        })

        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [email_to])
            response = email.send()
            verifier.message_sent = True
            verifier.save()
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response))
        except Exception as e:
            verifier.message_sent = False
            verifier.message_sent_details = str(e)
            verifier.save()
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))

    except Exception as e:

        print(e)
        Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = '', recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))

@shared_task(name="email_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def email_notifier(user_id, current_site, origin='', subject='', message='', email_to=[]):
    
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return

    try:
        
        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, email_to)
            response = email.send()
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response))
        except Exception as e:
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))
        
    except Exception as e:

        print(e)
        Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))

@shared_task(name="email_update_notifier", time_limit=7200, soft_time_limit=7200, max_retries=5)
def email_update_notifier(user_id, subject='', msg='', origin='', sign_off='', email_to=''):
    
    # reason we pass user_id instead of user object
    # kombu.exceptions.EncodeError: Object of type User is not JSON serializable
    try:
        user = get_user_model().objects.get(id=user_id)
    except Exception as e:
        print(e)
        return
        
    try:

        message = "Hi " + user.first_name + ", \n\n" + str(msg) + "\n\n" + "Regards,\n\n"+ sign_off

        try:
            email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [email_to])
            response = email.send()
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_DELIVERED, remote_message_status=str(response), status_response = str(response))
        except Exception as e:
            print(e)
            Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = message, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))

    except Exception as e:

        print(e)
        Message.objects.create(user=user, type=Message.MESSAGE_TYPE.EMAIL, subject=subject, message = msg, recipients = email_to, origin=origin, status=Message.TYPE.MESSAGE_UNDELIVERED, remote_message_status=str(e), status_response = str(e))