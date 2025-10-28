from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, \
    UsernameField
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
            msg = "Invio email per set/reset password a %s"%to_email
            add_log(level=2, custom_message=msg)
            print(msg)
            
            email_message = Mail(
                from_email = from_email,
                reply_to = from_email,
                to = [to_email] if to_email else [],
                template_subject = subject_template_name,
                template_txt = email_template_name,
                template_html = html_email_template_name,
                context=context,
            )

            email_message.save()
            # invio reale: può sollevare eccezioni del backend
            email_message.send()

        except Exception as exc:
            # log per debug/monitoring
            import traceback
            msg = "Errore durante invio email di reset a %s"%to_email
            add_log(level=4, custom_message=msg,exception=traceback.format_exc())
            traceback.print_exc()
            # aggiungo un errore al campo email (compare sotto l'input)
            self.add_error(
                "email",
                "Impossibile inviare l'email di reset. Controlla di aver inserito il giusto indirizzo " \
                    "altrimenti contatta l'assistenza."
            )

    
# class SignUpForm(UserCreationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder" : "Username",                
#                 "class": "form-control"
#             }
#         ))
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 "placeholder" : "Email",                
#                 "class": "form-control"
#             }
#         ))
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder" : "Password",                
#                 "class": "form-control"
#             }
#         ))
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder" : "Password check",                
#                 "class": "form-control"
#             }
#         ))

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')
