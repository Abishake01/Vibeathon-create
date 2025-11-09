"""
Test views for debugging
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import sys
from pathlib import Path

@api_view(['GET'])
def test_imports(request):
    """Test if all imports work correctly."""
    try:
        # Add app directory to path
        app_dir = Path(__file__).resolve().parent.parent / 'app'
        sys.path.insert(0, str(app_dir))
        
        from ai_providers import get_provider
        from ai_service import get_remaining_tokens
        
        return Response({
            "status": "success",
            "message": "All imports successful",
            "app_dir": str(app_dir),
            "app_dir_exists": app_dir.exists()
        })
    except Exception as e:
        import traceback
        return Response({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

