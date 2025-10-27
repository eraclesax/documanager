from typing import Any
from django import forms
from django.conf import settings
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UsernameField
from logger.utils import add_log
from mail.models import Mail

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder" : "Username",                
                "class": "form-control"
                }
            )
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder" : "Password",                
                "class": "form-control"
                }
            ),
    )
    remember_me = forms.BooleanField(
        label="Remember me",
        required=False,
        widget=forms.CheckboxInput(
            attrs={          
                "class": "custom-control-input"
                }
            ),
    )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "class": "form-control"
                }
            ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Ricostruisco l'invio dell'email così da poter intercettare l'errore
        e aggiungere un errore al form (self.add_error).
        """
        from django.template.loader import render_to_string
        try:
            msg = "Invio email per reset password a %s"%to_email
            add_log(level=2, custom_message=msg)
            print(msg)

            subject = None # Serve se no potrebbe arrabbiarsi nell'exception
            subject = render_to_string(subject_template_name, context)
            subject = "".join(subject.splitlines())
            body = render_to_string(email_template_name, context)

            # email_message = EmailMultiAlternatives(
            #     subject, body, from_email, [to_email]
            # )
            html_email = None
            if html_email_template_name is not None:
                html_email = render_to_string(html_email_template_name, context)
                
            email_message = Mail(
                subject=subject, 
                txt_text = body,
                reply_to = [to_email] if to_email else [],
                from_email = from_email,
                html_text = html_email
            )

            print("SONO QUI------------------")
            email_message.save()
            # invio reale: può sollevare eccezioni del backend
            email_message.send()
            return True

        except Exception as exc:
            # log per debug/monitoring
            import traceback
            msg = "Errore durante invio email di reset a %s"%to_email
            add_log(level=4, custom_message=msg,exception=traceback.format_exc())
            traceback.print_exc()
            # aggiungo un errore al campo email (compare sotto l'input)
            self.add_error(
                "email",
                "Impossibile inviare l'email di reset. Riprovare più tardi o contattare l'assistenza."
            )
            # ritorno False per segnalare al chiamante che c'è stato un problema
            return False


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password check",                
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
