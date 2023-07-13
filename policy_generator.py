# import json
import copy

LIFECYCLE_POLICY_TEMPLATE = {
    'rules': [
    ]
}

RULE_POLICY = {
    'action': {
        'type': 'expire'
    },
    'selection': {
        'countType': 'imageCountMoreThan',
        'countNumber': 5,
        'tagStatus': 'tagged',
        'tagPrefixList': [
          'v1'
        ]
    },
    'description': 'V1 Test',
    'rulePriority': 1
}


def generate_lifecycle_policy_json(versions) -> dict:
    priority = 1
    for version in versions.split(','):
        rule_policy_copy = copy.deepcopy(RULE_POLICY)
        rule_policy_copy['selection']['tagPrefixList'][0] = version.strip()
        rule_policy_copy['description'] = f'{version.strip().upper()} Test'
        rule_policy_copy['rulePriority'] = priority
        LIFECYCLE_POLICY_TEMPLATE.get('rules').append(rule_policy_copy)
        priority += 1

    return copy.deepcopy(LIFECYCLE_POLICY_TEMPLATE)

    # with open('test_json.json', 'w') as wf:
    #     json.dump(LIFECYCLE_POLICY_TEMPLATE, wf, indent=4)

# with open('versions.txt', 'r') as f:
#     priority = 1
#     for line in f.readlines():
#         RULE_POLICY_COPY = copy.deepcopy(RULE_POLICY)
#         RULE_POLICY_COPY['selection']['tagPrefixList'][0] = line.strip()
#         RULE_POLICY_COPY['description'] = f'{line.strip().upper()} Test'
#         RULE_POLICY_COPY['rulePriority'] = priority
#         LIFECYCLE_POLICY_TEMPLATE.get('rules').append(RULE_POLICY_COPY)
#         priority += 1
#
