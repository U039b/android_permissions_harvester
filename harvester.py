from methods_extractor import extract_required_permissions_from_sources
from permissions_extractor import extract_groups_and_permissions
import json
from textblob import TextBlob

aosp_root_dir = './aosp/'
locale = 'fr'
output_dir = './output'

# permissions = extract_groups_and_permissions(aosp_root_dir, locale, output_dir)
# methods = extract_required_permissions_from_sources('{}'.format(aosp_root_dir))
#
# for method_name, method in methods.items():
#     for permission in method['permissions']:
#         permission_name = 'android.permission.{}'.format(permission['member'])
#         if permission_name in permissions['permissions']:
#             if 'methods' not in permissions['permissions'][permission_name]:
#                 permissions['permissions'][permission_name]['methods'] = []
#             permissions['permissions'][permission_name]['methods'].append(
#                 {
#                     'method_name': method_name,
#                     'documentation': method['documentation'],
#                     'file': method['file'],
#                     'line': method['line'],
#                 }
#             )
#         else:
#             print('Undefined permission {}'.format(permission_name))
#
# with open('{}/out.json'.format(output_dir), 'w') as j:
#     json.dump(permissions, j, indent=2)

permissions = {}
with open('{}/out.json'.format(output_dir), 'r') as j:
    permissions = json.load(j)

for permission in permissions['permissions']:
    if 'methods' not in permissions['permissions'][permission]:
        continue
    for method in permissions['permissions'][permission]['methods']:
        en_blob = TextBlob(''.join(method['documentation'].splitlines()))
        if en_blob.sentences:
            s = en_blob.sentences[0]
            print('>>', s.translate(to='fr'))

