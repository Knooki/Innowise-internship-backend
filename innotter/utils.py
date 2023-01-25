from django.http import JsonResponse


def create_exception_response(exp_cl) -> JsonResponse:
    exp = exp_cl()
    return JsonResponse(exp.get_full_details(), status=exp_cl.status_code)
