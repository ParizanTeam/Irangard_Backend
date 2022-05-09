from accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    is_owner = serializers.SerializerMethodField('get_is_owner')
    
    class Meta:
        model = User
        fields = ['full_name', 'is_special', 'email', 'image', 'username', 'about_me', 'is_owner', 'following_number', 'follower_number']
        read_only_fields = ('email', 'following_number', 'follower_number', 'is_owner')
        
    def get_is_owner(self, user):
        request_user = self.context['user']
        if str(request_user) == str(user.username):
            return True
        else:
            return False

class UserFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
    
   
        
    
    
    
        

