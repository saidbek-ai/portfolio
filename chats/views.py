# from django.contrib.auth.decorators import login_required, user_passes_test 
# from django.shortcuts import render, redirect, get_object_or_404
# # from django.http import HttpResponse
# # from django.db.models import Q
# from django.utils import timezone
# from .models import Chat, Message
# from .forms import SendMessageForm

# # Load chat for current user (user view)
# @login_required
# def chat_page(request):
    
#     if request.user.is_staff :
#         return redirect("chat:staff_chat")
#     else:     
#         return redirect("chat:user_chat")


# @login_required
# @user_passes_test(lambda u: not u.is_staff)
# def user_view(request):
#     try:
#         chat = Chat.objects.get(user=request.user)
#     except Chat.DoesNotExist:
#         chat = {"id": 0}

#     form = SendMessageForm()
#     if request.method == "POST":
#         chat, _ = Chat.objects.get_or_create(user=request.user)

#         print("📬 POST received from user!")
#         form = SendMessageForm(request.POST)


#         if form.is_valid():
#             message = form.save(commit=False)
#             message.chat = chat
#             message.sender = request.user
#             message.save()

#             chat.updated_at = timezone.now()
#             chat.save()

#             return render(request, "chats/partials/_message_item.html", {"chat":chat, "msg":message})
        
#     else:
#         form = SendMessageForm()


#     return render(request, "chats/user_page.html", {"form":form,"chat": chat})


# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def staff_view(request):
#     chats = Chat.objects.all().order_by("-updated_at")[:40]

#     for chat in chats:
#         chat.unread_count = chat.unread_messages(request.user)

#     form = SendMessageForm()
#     if request.method == "POST":
#         chat_id = request.POST.get("chat_id")
#         print(chat_id)


#         chat = get_object_or_404(Chat, id=chat_id)

#         print("📬 POST received from staff!")
#         form = SendMessageForm(request.POST)

#         if form.is_valid():
#             message = form.save(commit=False)
#             message.chat = chat
#             message.sender = request.user
#             message.save()

#             chat.updated_at = timezone.now()
#             chat.save()

#             return render(request, "chats/partials/_message_item.html", {"chat":chat, "msg":message})

#     else:
#         form = SendMessageForm()

#     return render(request, "chats/staff_page.html", {"chats":chats, "form":form})



# @login_required
# def get_messages(request, chat_id):

#     if chat_id == 0:
#         messages = []
#         chat = None
#         first_unread_id = None
#     else:
#         chat = get_object_or_404(Chat, id=chat_id)
#         messages = chat.messages.select_related("sender").order_by("created_at")[:30]

#         if chat:   # Find index of first unread message
#             first_unread_id = None
#             for msg in messages:
#                 if not msg.read and msg.sender != request.user:
#                     first_unread_id = msg.id
#                     break

#     if request.user.is_staff:

#         # print(chat)
#         # print(messages)
#         # print(first_unread_id)

#         print("getting messages as staff")
#         return render(request, "chats/partials/_staff_conversation.html", {"selected_chat": chat, "messages":messages,"first_unread_id":first_unread_id})
#     else:
#         print("getting messages as user")

#         return render(request, "chats/partials/_messages_list.html", {"messages":messages,"first_unread_id":first_unread_id})

# def load_older_messages(request, chat_id, before_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     messages = chat.messages.filter(id__lt=before_id).order_by('-created_at')[:30]
#     return render(request, "chat/partials/_messages_chunk.html", {
#         "messages": reversed(messages),
#     })

# def load_newer_messages(request, chat_id, after_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     messages = chat.messages.filter(id__gt=after_id).order_by('created_at')[:30]
#     return render(request, "chat/partials/_messages_chunk.html", {
#         "messages": messages,
#     })

import logging
from django.contrib.auth import authenticate, login, get_user_model
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, now
from django.db.models import Q
from django.db.models.functions import Lower
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import IsNotStaff, IsStaffORSuperUser
from .models import Chat, Message
from .serializers import UserSerializer, ChatSerializer, MessageSerializer

from .utils import msg_event

logger = logging.getLogger(__name__)

User = get_user_model()


# dev views start here
@api_view(["GET"])
def dev_user_info(request):
    # Only allow in dev
    if not settings.DEBUG:
        return Response({"error": "Not allowed in production"}, status=403)
    
    
    user = request.user
    return Response({
        "is_authenticated": user.is_authenticated,
        "username": user.username if user.is_authenticated else None,
        "is_staff": user.is_staff,
        "id": user.id
    })


@api_view(["POST"])
def dev_login(request):

    if not settings.DEBUG:
        return Response({"error": "Not allowed in production"}, status=403)

    data = request.data
    user = authenticate(email=data["email"], password=data["password"])
    if user:
        login(request, user)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "failed"}, status=status.HTTP_403_FORBIDDEN)
# End of dev views


# dev base view
def base_view(request):
    return redirect("http://localhost:5173/")

# only for users to get their chat 
class UserViewAPI(APIView):
    permission_classes = [IsNotStaff]

    def get(self, request):
        try:
            chat, _ = Chat.objects.get_or_create(user=request.user)
        except Chat.DoesNotExist:
            return Response({"detail": "No chat found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChatSerializer(chat, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        chat, _ = Chat.objects.get_or_create(user=request.user)
        idemp_key = request.headers.get("Idempotency-Key")

        if not idemp_key:
            return Response({"error": "Missing idempotency key"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"idempotency:{idemp_key}"
        lock_key = f"idempotency_lock:{idemp_key}"

        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)
        
        if not cache.add(lock_key, "processing", timeout=10):
             return Response({"error": "Request already processing"}, status=status.HTTP_409_CONFLICT)
        
        try:
            serializer = MessageSerializer(data=request.data)

            print(f"user {chat.id}")
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save(sender=request.user, chat=chat, idempotency_key=idemp_key)
                    #No receiver_id requiered to send msg to staff
                    msg_event(event_type="new", payload=serializer.data)


                cache.set(cache_key, serializer.data, timeout=60 * 3)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"[UserViewAPI: post()] Serializer error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"[UserViewAPI: post()] Unexpected error: {e}", exc_info=True)
            return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            #  === Crucial part for releasing future requests ===
            # Cache lock must be removed not to block other requests
            cache.delete(lock_key)



class AdminChatViewAPI(APIView):
    permission_classes = [IsStaffORSuperUser]
    
    def get(self, request):
        chats = Chat.objects.select_related('user').all().order_by("-updated_at")
        serializer = ChatSerializer(chats, context={"request": request}, many=True)

        return Response({"chats":serializer.data}, status=status.HTTP_200_OK)
    

class AdminContactsViewAPI(APIView):
    permission_classes = [IsStaffORSuperUser]

    def get(self, request):
        after_first_name = request.query_params.get("after_first_name")
        after_id = request.query_params.get("after_id")
        search_q = request.query_params.get("search_q")

        try:
            limit = int(request.query_params.get("limit", 100))
            limit = max(10, min(limit, 500))
        except (ValueError, TypeError):
            limit = 100

        try:
            after_id = int(after_id) if after_id else None

            qs = User.objects.all()

            # Apply search filter first
            if search_q:
                qs = qs.filter(
                    Q(first_name__icontains=search_q) |
                    Q(first_name__icontains=search_q)
                )

            # Apply cursor pagination
            if after_first_name and after_id:
                qs = qs.filter(
                    Q(first_name__gt=after_first_name) |
                    Q(first_name=after_first_name, id__gt=after_id)
                )

            # Order alphabetically
            qs = qs.order_by(Lower("first_name"), "id")

            contacts = list(qs[:limit])

            serializer = UserSerializer(contacts, many=True)

            # Prepare next cursor
            if contacts:
                last_contact = contacts[-1]
                next_cursor = {
                    "after_first_name": last_contact.first_name,
                    "after_id": last_contact.id
                }
            else:
                next_cursor = None

            return Response({
                "results": serializer.data,
                "next_cursor": next_cursor
            }, status=200)

        except Exception as e:
            logger.warning(
                "[AdminContactsViewAPI: get()] fetch contacts error",
                exc_info=e
            )
            return Response(
                {"error": "Fetch contacts failed!"},
                status=400
            )
        


# only for staff members to get messages by chat id
class SelectedChatAPI(APIView):
    permission_classes = [IsStaffORSuperUser]

    def get_chat(self, chat_id):
        try:
            return Chat.objects.select_related('user').get(id=chat_id)
        except Chat.DoesNotExist:
            return None

    def get(self, request, chat_id):
        chat = self.get_chat(chat_id)
        if not chat:
            return Response({"detail": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatSerializer(chat, context={"request": request})
        serialized_chat_id = serializer.data.get('id')
        serialized_chat_user = serializer.data.get('user')
        return Response({'id': serialized_chat_id, 'user': serialized_chat_user}, status=status.HTTP_200_OK)

        # return Response({"id": chat.id, "user": chat.user,},)

        
    def post(self, request, chat_id):
        chat = self.get_chat(chat_id)
        idemp_key = request.headers.get("Idempotency-Key")

        if not chat:
            return Response({"detail": "No chat found."}, status=status.HTTP_404_NOT_FOUND)

        if not idemp_key:
            return Response({"error": "Missing idempotency key"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"idempotency:{idemp_key}"
        lock_key = f"idempotency_lock:{idemp_key}"

        # 1️⃣ Check cache for already processed result
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        # 2️⃣ Try to acquire a lock for processing
        if not cache.add(lock_key, "processing", timeout=10):
            # throttling half second
            # time.sleep(0.5)
            # final = cache.get(cache_key)
            # if final:
            #     return Response(final, status=status.HTTP_200_OK)

            # Someone else is processing this idempotency key
            return Response({"error": "Request already processing"}, status=status.HTTP_409_CONFLICT)

        # 3️⃣ Proceed to create the message atomically
        try:
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save(
                        sender=request.user,
                        chat=chat,
                        idempotency_key=idemp_key
                    )

                    msg_event(event_type="new", payload=serializer.data, receiver_id=chat.user.id)

                # Cache the successful result
                cache.set(cache_key, serializer.data, timeout=60 * 3)  # Keep for 5 mins
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # Validation failed
            logger.warning(f"[SelectedChatAPI: post()] Serializer error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"[SelectedChatAPI: post()] Unexpected error: {e}", exc_info=True)
            return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            #  === Crucial part for releasing future requests ===
            # Cache lock must be removed not to block other requests
            cache.delete(lock_key)
        


# view to get messages for both users and staff members
class MessagesAPI(APIView): 
    permission_classes= [IsAuthenticated]

    # get messages ## rechecking is required
    def get(self, request, chat_id):
        #query
        after = request.query_params.get("after", None)
        before = request.query_params.get("before", None)
        anchor_id=None

        try:
            messages_limit = max(10, int(request.query_params.get("limit", 50)))
        except ValueError:
            messages_limit = 50

        has_more_older = has_more_newer = False
        # get CHAT by user type
        if request.user.is_staff:
            # chat = Chat.objects.get(id=chat_id)
            chat = get_object_or_404(Chat, id=chat_id)
        else:
            chat = get_object_or_404(Chat, user=request.user)
            
        
        #GET MESSAGE BY QUERY
        #get NEWER messages
        if after:
            try:
                after_dt = parse_datetime(after)
                if after_dt is None:
                    raise ValueError("Invalid timestamp")
                
                if is_naive(after_dt):
                    after_dt = make_aware(after_dt)
 
                messages_qs = Message.objects.filter(chat=chat, created_at__gt=after_dt, deleted_at__isnull=True).order_by("created_at")[:messages_limit]
                messages = list(messages_qs)

                has_more_older =  Message.objects.filter(chat=chat, created_at__lt=messages[0].created_at, deleted_at__isnull=True).exists() if messages else False
                has_more_newer = Message.objects.filter(chat=chat, created_at__gt=messages[-1].created_at, deleted_at__isnull=True).exists() if messages else False
            except Exception:
                return Response({"error": "Invalid 'after' timestamp"}, status=status.HTTP_400_BAD_REQUEST)

        #get OLDER messages
        elif before:
            try:
                before_dt = parse_datetime(before)
                if before_dt is None:
                    raise ValueError("Invalid timestamp")
                
                if is_naive(before_dt):
                    before_dt = make_aware(before_dt)

                messages_qs = Message.objects.filter(chat=chat, created_at__lt=before_dt, deleted_at__isnull=True).order_by('-created_at')[:messages_limit]
                messages = list(messages_qs)[::-1]

                has_more_older = Message.objects.filter(chat=chat, created_at__lt=messages[0].created_at, deleted_at__isnull=True).exists() if messages else False
                has_more_newer = Message.objects.filter(chat=chat, created_at__gt=messages[-1].created_at, deleted_at__isnull=True).exists() if messages else False
            except Exception:
                return Response({"error": "Invalid timestamp"}, status=status.HTTP_400_BAD_REQUEST)
            
        #get INITIAL messages
        else:
            unread = Message.objects.filter(chat=chat, read=False, deleted_at__isnull=True).order_by('created_at')[:int(messages_limit / 2)]

            print("has_unread_messages",unread.exists())
        
            if unread.exists():
                unread = list(unread) # to get last message item of unread
                remained_limit = messages_limit - len(unread)
                read_qs = Message.objects.filter(chat=chat, read=True, deleted_at__isnull=True).order_by('-created_at')[:remained_limit]
                read = list(read_qs)
                #combine messages
                messages = sorted(unread + read, key=lambda m: m.created_at)
            else:
                read_qs = Message.objects.filter(chat=chat, read=True, deleted_at__isnull=True).order_by('-created_at')[:messages_limit]
                read = list(read_qs[::-1])
                messages = read

            has_more_older =  Message.objects.filter(chat=chat, created_at__lt=messages[0].created_at, deleted_at__isnull=True).exists() if read else False
            has_more_newer = Message.objects.filter(chat=chat, created_at__gt=messages[-1].created_at, deleted_at__isnull=True).exists() if unread else False

        # reversed_messages = messages[::-1]
        # initial_anchor_id = {"initial_anchor_id": anchor_id} if anchor_id else {}
        serializer = MessageSerializer(messages, many=True)
        return Response({"messages": serializer.data, "has_more_older": has_more_older, "has_more_newer": has_more_newer}, status=status.HTTP_200_OK)
    

    # Read messages ##pr
    def post(self, request, chat_id):
        data = request.data
        last_seen_msg_id= data.get("last_seen_id", None)

        if not all([chat_id, last_seen_msg_id]):
            return Response({"error": "chatId and last_seen_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate types
        try:
            chat_id = int(chat_id)
            last_seen_msg_id = int(last_seen_msg_id)
        except (ValueError, TypeError):
            return Response({"error": "IDs must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(Chat.objects.select_related("user"), id=chat_id)

        # Access check: Ensure user is member of chat or staff
        if not (request.user.is_staff or request.user == chat.user):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        


        queryset = Message.objects.select_related("sender").filter(
            chat=chat,
            id__lte=last_seen_msg_id,
            read=False
        ).exclude(sender=request.user)

        if request.user.is_staff:
            queryset = queryset.filter(sender__is_staff=False)
        

        with transaction.atomic():
            if queryset.exists():

                # msg id must be the highest to client side work properly
                last_read_msg = dict(queryset.values("idempotency_key", "id").last())
                read_count = queryset.update(read=True)
            else:
                last_read_msg = dict()
                read_count = 0

            receiver_id = chat.user.id if request.user.is_staff else None

            res = {"last_read_msg":last_read_msg, "read_count": read_count, "chat_id": chat_id}
            msg_event(event_type="read", payload=res, receiver_id=receiver_id)


        # don't change variables (read_ids, read_count) it breaks client side read logic
        return Response(res, status=status.HTTP_200_OK)
        # return Response({"updated_count": read_count, "updated_ids": updated_ids}, status=status.HTTP_200_OK)


    # delete messages ##pr
    def delete(self, request, chat_id):
        ids = request.data.get("ids", [])

        if not isinstance(ids, list):
            return Response({"error": "Expected 'ids' to be a list"}, status=status.HTTP_400_BAD_REQUEST )
        
        if not ids:
            return Response({"deleted": 0, "deleted_ids": []}, status=status.HTTP_200_OK)
        
        chat = get_object_or_404(Chat.objects.select_related('user'), id=chat_id)
        
        
        if not (request.user.is_staff or chat.user == request.user):
            return Response({"error": "You don't have permission to delete messages in this chat!"}, status=status.HTTP_403_FORBIDDEN)
        

        qs = Message.objects.filter(id__in=ids, sender=request.user, chat=chat, deleted_at__isnull=True)

        with transaction.atomic():
            if qs.exists():
                deleted_ids = list(qs.values_list("id", flat=True))  # get ids first
                deleted_count = qs.update(deleted_at=now())
            else:
                deleted_ids = list()
                deleted_count = 0

            receiver_id = chat.user.id if request.user.is_staff else None

            res = {"deleted_count": deleted_count, "deleted_ids": deleted_ids, "chat_id": chat_id}
            msg_event(event_type="delete", payload=res, receiver_id=receiver_id)

        return Response(res, status=status.HTTP_200_OK)
    
        # request obj example from front end: {"ids": [101, 102, 103] }
    

    # update text-message ##pr
    def patch(self, request, chat_id):
        msg_id = request.data.get("msg_id", None)
        updated_text = request.data.get("updated_text", None)

        if updated_text is not None:
            updated_text = updated_text.strip()

        if not all([updated_text, msg_id]):
            return Response({"error": "msg_id and non-empty updated_text are required!"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_id = int(chat_id)
            msg_id = int(msg_id)
        except (ValueError, TypeError):
            return Response({"error": "IDs must be integers."}, status=status.HTTP_400_BAD_REQUEST)
        
        chat = get_object_or_404(Chat.objects.select_related("user"), id=chat_id)

        # Access check: Ensure user is member of chat or staff
        if not (request.user.is_staff or request.user == chat.user):
            return Response({"error": "You don't have permission to update message in this chat!"}, status=status.HTTP_403_FORBIDDEN)

        msg = get_object_or_404(Message, id=msg_id, chat=chat, sender=request.user)

        try:
            with transaction.atomic():

                msg.text = updated_text
                msg.updated_at = now()
                msg.save(update_fields=["text", "updated_at"])
                msg.refresh_from_db()

                # receiver_id = chat.user.id if request.user.is_staff else None
                # msg_event("edit", payload=msg, receiver_id=receiver_id)

        except Exception as err:
            return Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MessageSerializer(msg, context={"request": request})
        receiver_id = chat.user.id if request.user.is_staff else None
        msg_event("edit", payload=serializer.data, receiver_id=receiver_id)
        
        return Response({"updated_msg": serializer.data}, status=status.HTTP_200_OK)


        