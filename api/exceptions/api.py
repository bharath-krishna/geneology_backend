class APIError(Exception):
    def __init__(self, key, status_code=None, **params):
        Exception.__init__(self)
        # error_obj = ErrorMessages(key, **params)
        # self.reason = error_obj.reason
        # self.message = error_obj.message
        self.reason = 'reason'
        self.message = 'message'
        if status_code is None:
            # default
            self.status_code = 400
        else:
            self.status_code = status_code

    def to_response(self):
        response = jsonify({'reason': self.reason, 'body': {'message': self.message, }})
        response.status_code = self.status_code
        return response

# class ErrorMessages:
    
#     ERRORS = {
#         # tuple of reason, message
#         'unauthorized': (
#             401,
#             _gt('Unauthorized'),
#             _gt('Unauthorized'),
#         ),
#         'unauthorized_w_msg': (
#             401,
#             _gt('Unauthorized'),
#             _gt('%(text)s'),
#         ),
#         'authorization_error': (
#             403,
#             _gt('Authorization error'),
#             _gt('%(text)s'),
#         ),
#         'not_found': (
#             404,
#             _gt('Not found'),
#             _gt('%(field)s "%(value)s" does not exist'),
#         ),
#         'not_found_general': (
#             404,
#             _gt('Not found'),
#             _gt('%(value)s not found'),
#         ),
#         # unlike other not found errors this one returns 400 to show that user try invalid resource access.
#         'not_found_resource': (
#             400,
#             _gt('Not found'),
#             _gt('%(field)s "%(value)s" does not exist'),
#         ),
#         'missing_field': (
#             404,
#             _gt('Missing field'),
#             _gt('%(field)s field is missing'),
#         ),
#         'required_list': (
#             400,
#             _gt('Required field'),
#             _gt('Please select at least one %(field)s'),
#         ),
#         'required_field': (
#             400,
#             _gt('Required field'),
#             _gt('%(field)s can not be empty'),
#         ),
#         'invalid_field': (
#             400,
#             _gt('Invalid field'),
#             _gt('Please enter valid "%(field)s"'),
#         ),
#         'invalid_field_value': (
#             400,
#             _gt('Invalid value'),
#             _gt('Field: "%(field)s" has invalid value: "%(value)s"'),
#         ),
#         'invalid_field_value_with_expected': (
#             400,
#             _gt('Invalid value'),
#             _gt('Field: "%(field)s" has invalid value: "%(value)s". %(expected_note)s'),
#         ),
#         'invalid_value': (
#             400,
#             _gt('Invalid value'),
#             _gt('Please enter valid post data. "%(value)s"'),
#         ),
#         'duplicated_resource': (
#             409,
#             _gt('Duplicated resource'),
#             _gt('Duplicated %(value)s object'),
#         ),
#         'conflicted_with_detail': (
#             409,
#             _gt('Duplicated resource'),
#             _gt('Duplicated %(value)s object. %(text)s'),
#         ),
#         'general_error': (
#             400,
#             _gt('Error'),
#             _gt('%(text)s'),
#         ),
#     }

#     def __init__(self, key, **params):
#         self.key = key
#         self.params = params

#     @property
#     def status_code(self):
#         return self.ERRORS[self.key][0]

#     @property
#     def reason(self):
#         return self.ERRORS[self.key][1]

#     @property
#     def message(self):
#         error_message = self.ERRORS[self.key][2]
#         # apply text arguments
#         return error_message % self.params
