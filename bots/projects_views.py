from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Bot, BotStates, Bot, Credentials, RecordingStates, Utterance
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponse
from .models import ApiKey, WebhookConfiguration, WebhookTypes
from django.db import models, IntegrityError

class ProjectUrlContextMixin:
    def get_project_context(self, object_id, project):
        return {
            'project': project,
        }

class ProjectDashboardView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id):
        try:
            project = get_object_or_404(Project, 
                object_id=object_id,
                organization=request.user.organization
            )
        except:
            return redirect('/')
            
        # Quick start guide status checks
        zoom_credentials = Credentials.objects.filter(
            project=project,
            credential_type=Credentials.CredentialTypes.ZOOM_OAUTH
        ).exists()
        
        deepgram_credentials = Credentials.objects.filter(
            project=project,
            credential_type=Credentials.CredentialTypes.DEEPGRAM
        ).exists()
        
        has_api_keys = ApiKey.objects.filter(project=project).exists()
        
        has_ended_bots = Bot.objects.filter(
            project=project,
            state=BotStates.ENDED
        ).exists()
        
        context = self.get_project_context(object_id, project)
        context.update({
            'quick_start': {
                'has_credentials': zoom_credentials and deepgram_credentials,
                'has_api_keys': has_api_keys,
                'has_ended_bots': has_ended_bots,
            }
        })
        
        return render(request, 'projects/project_dashboard.html', context)

class ProjectApiKeysView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        context = self.get_project_context(object_id, project)
        context['api_keys'] = ApiKey.objects.filter(project=project).order_by('-created_at')
        return render(request, 'projects/project_api_keys.html', context)

class CreateApiKeyView(LoginRequiredMixin, View):
    def post(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        name = request.POST.get('name')
        
        if not name:
            return HttpResponse("Name is required", status=400)
            
        api_key_instance, api_key = ApiKey.create(project=project, name=name)
        
        # Render the success modal content
        return render(request, 'projects/partials/api_key_created_modal.html', {
            'api_key': api_key,
            'name': name
        })

class DeleteApiKeyView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def delete(self, request, object_id, key_object_id):
        api_key = get_object_or_404(ApiKey, 
            object_id=key_object_id,
            project__organization=request.user.organization
        )
        api_key.delete()
        context = self.get_project_context(object_id, api_key.project)
        context['api_keys'] = ApiKey.objects.filter(project=api_key.project).order_by('-created_at')
        return render(request, 'projects/project_api_keys.html', context)

class RedirectToDashboardView(LoginRequiredMixin, View):
    def get(self, request, object_id, extra=None):
        return redirect('bots:project-dashboard', object_id=object_id)

class CreateCredentialsView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def post(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )

        try:
            credential_type = int(request.POST.get('credential_type'))
            if credential_type not in [choice[0] for choice in Credentials.CredentialTypes.choices]:
                return HttpResponse('Invalid credential type', status=400)

            # Get or create the credential instance
            credential, created = Credentials.objects.get_or_create(
                project=project,
                credential_type=credential_type
            )

            # Parse the credentials data based on type
            if credential_type == Credentials.CredentialTypes.ZOOM_OAUTH:
                credentials_data = {
                    'client_id': request.POST.get('client_id'),
                    'client_secret': request.POST.get('client_secret')
                }
                
                if not all(credentials_data.values()):
                    return HttpResponse('Missing required credentials data', status=400)

            elif credential_type == Credentials.CredentialTypes.DEEPGRAM:
                credentials_data = {
                    'api_key': request.POST.get('api_key')
                }
                
                if not all(credentials_data.values()):
                    return HttpResponse('Missing required credentials data', status=400)

            else:
                return HttpResponse('Unsupported credential type', status=400)

            # Store the encrypted credentials
            credential.set_credentials(credentials_data)

            # Return the entire settings page with updated context
            context = self.get_project_context(object_id, project)
            context['credentials'] = credential.get_credentials()
            context['credential_type'] = credential.credential_type
            if credential.credential_type == Credentials.CredentialTypes.ZOOM_OAUTH:
                return render(request, 'projects/partials/zoom_credentials.html', context)
            elif credential.credential_type == Credentials.CredentialTypes.DEEPGRAM:
                return render(request, 'projects/partials/deepgram_credentials.html', context)

        except Exception as e:
            return HttpResponse(str(e), status=400)

class ProjectSettingsView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        
        # Try to get existing credentials
        zoom_credentials = Credentials.objects.filter(
            project=project,
            credential_type=Credentials.CredentialTypes.ZOOM_OAUTH
        ).first()

        deepgram_credentials = Credentials.objects.filter(
            project=project,
            credential_type=Credentials.CredentialTypes.DEEPGRAM
        ).first()

        webhook_configurations = WebhookConfiguration.objects.filter(project=project).order_by('-created_at')

        context = self.get_project_context(object_id, project)
        context.update({
            'zoom_credentials': zoom_credentials.get_credentials() if zoom_credentials else None,
            'zoom_credential_type': Credentials.CredentialTypes.ZOOM_OAUTH,
            'deepgram_credentials': deepgram_credentials.get_credentials() if deepgram_credentials else None,
            'deepgram_credential_type': Credentials.CredentialTypes.DEEPGRAM,
            'webhook_configurations': webhook_configurations,
            'webhook_types': WebhookTypes,
        })
        
        return render(request, 'projects/project_settings.html', context)
    
class ProjectBotsView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        
        bots = Bot.objects.filter(project=project).order_by('-created_at')

        context = self.get_project_context(object_id, project)
        context.update({
            'bots': bots,
            'BotStates': BotStates,
        })
        
        return render(request, 'projects/project_bots.html', context)
    
class ProjectBotDetailView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id, bot_object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        
        bot = get_object_or_404(Bot, 
            object_id=bot_object_id,
            project=project
        )

        # Prefetch recordings with their utterances and participants
        bot.recordings.all().prefetch_related(
            models.Prefetch(
                'utterances',
                queryset=Utterance.objects.select_related('participant')
            )
        )

        context = self.get_project_context(object_id, project)
        context.update({
            'bot': bot,
            'BotStates': BotStates,
            'RecordingStates': RecordingStates,
        })
        
        return render(request, 'projects/project_bot_detail.html', context)
    
class ProjectWebhooksView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def get(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        context = self.get_project_context(object_id, project)
        context['webhook_configurations'] = WebhookConfiguration.objects.filter(
            project=project
        ).order_by('-created_at')
        context['webhook_types'] = WebhookTypes
        return render(request, 'projects/project_webhooks.html', context)

class CreateWebhookView(LoginRequiredMixin, View):
    def post(self, request, object_id):
        project = get_object_or_404(Project, 
            object_id=object_id,
            organization=request.user.organization
        )
        
        webhook_type = request.POST.get('webhook_type')
        destination_url = request.POST.get('destination_url')
        
        if not webhook_type or not destination_url:
            return HttpResponse("Webhook type and destination URL are required", status=400)
            
        try:
            webhook_type = int(webhook_type)
            if webhook_type not in [choice[0] for choice in WebhookTypes.choices]:
                return HttpResponse('Invalid webhook type', status=400)
        except ValueError:
            return HttpResponse('Invalid webhook type', status=400)

        try:
            WebhookConfiguration.objects.create(
                project=project,
                webhook_type=webhook_type,
                destination_url=destination_url
            )
            
            # Return the updated webhook list instead of a modal
            context = {
                'project': project,
                'webhook_configurations': WebhookConfiguration.objects.filter(
                    project=project
                ).order_by('-created_at'),
                'webhook_types': WebhookTypes
            }
            return render(request, 'projects/partials/webhook_configurations.html', context)
        except IntegrityError:
            return HttpResponse(
                "A webhook with this type and destination URL already exists", 
                status=400
            )

class DeleteWebhookView(LoginRequiredMixin, ProjectUrlContextMixin, View):
    def delete(self, request, object_id, hook_object_id):
        webhook = get_object_or_404(WebhookConfiguration, 
            object_id=hook_object_id,
            project__organization=request.user.organization
        )
        webhook.delete()
        
        context = self.get_project_context(object_id, webhook.project)
        context['webhook_configurations'] = WebhookConfiguration.objects.filter(
            project=webhook.project
        ).order_by('-created_at')
        context['webhook_types'] = WebhookTypes
        return render(request, 'projects/partials/webhook_configurations.html', context)