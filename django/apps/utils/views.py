from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from django.apps import apps
# Create your views here.

import string
from random import randint, choice

def get_field_choices(named):
    """
    Get choices from namedtuple
    """
    dictionary = named._asdict()
    return [(v, k) for (k, v) in dictionary.items()]


def random_generator(length=5, letters=True, digits=False, punctuation=False, exclude=[], app_label=None, model_name=None, field_name=None):
    '''
    Create random string
    leave_out - list of string charecters to leave out e.g [':', '<', '8'] 
    '''
    
    allchar = ''

    if letters:
        allchar = string.ascii_letters 
    if digits:
        allchar += string.digits 
    if punctuation:
        allchar += string.punctuation

    if not letters and not digits and not punctuation:
        allchar = string.ascii_letters

    generator = "".join(choice(allchar) for x in range(randint(length, length)) if str(x) not in exclude)
    
    return generator
    
# def check_if_object_exists(app_label=None, model_name=None, field_name=None, object=None):
#     """
#     Check if object exists in a table based on field name
#     """

#     try:
#         model = apps.get_model(app_label=app_label, model_name=model)
#         field = model._meta.get_field('field_name')
#         # field.value_from_object(object)
#         if getattr(object, ):
#             return True
#         else:
#             return False
#     except:
#         return False


#     if model_name:
#         if check_if_object_exists(app_label=None, model_name=None, field_name=None, object=generator):
#             return random_generator(length=length, letters=letters, digits=digits, punctuation=punctuation, replace=replace, app_label=app_label, model=model)
    
#     return generator