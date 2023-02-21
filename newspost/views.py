from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import CustomUserCreationForm
from .models import NewsPost, Reporter
from .tokens import account_activation_token


# View to display a list of all news posts
class NewsPostListView(ListView):
    model = NewsPost
    template_name = 'newspost/newspost_list.html'

# View to display the details of a single news post
def news_detail(request, pk):
    news_post = get_object_or_404(NewsPost, pk=pk)
    return render(request, 'newspost/newspost_detail.html', {'news_post': news_post})

# View to create a new news post
class NewsPostCreateView(CreateView):
    model = NewsPost
    fields = ['title', 'content', 'reporter', 'image']
    template_name = 'newspost/news_form.html'
    success_url = reverse_lazy('newspost_list')

    # Get the currently logged in user and assign them as the reporter for the news post
    def form_valid(self, form):
        form.instance.reporter = self.request.user.reporter
        return super().form_valid(form)

# View to display a list of all reporters
class ReporterListView(ListView):
    model = Reporter
    template_name = 'newspost/reporter_list.html'

# View to add a reporter to the current user's favorites list
@login_required
def add_reporter_favorite(request, pk):
    reporter = get_object_or_404(Reporter, pk=pk)
    request.user.reporter.favorites.add(reporter)
    return redirect('reporter_list')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # current_site = get_current_site(request)
            mail_subject = 'Activate your News Portal account.'
            token = account_activation_token.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': '127.0.0.1', #current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'activation_link': f'http://127.0.0.1:9000/activate/{uidb64}/{token}'
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send()
            return redirect('account_activation_sent')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'registration/activation_error.html')


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')
