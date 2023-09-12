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


def generate_lifecycle_policy_json(versions: list, number_of_images_to_keep: int) -> dict:
    priority = 1
    for version in versions:
        rule_policy_copy = copy.deepcopy(RULE_POLICY)
        rule_policy_copy['selection']['tagPrefixList'][0] = version.strip()
        rule_policy_copy['selection']['countNumber'] = number_of_images_to_keep
        rule_policy_copy['description'] = f'{version.strip()} Test'
        rule_policy_copy['rulePriority'] = priority
        LIFECYCLE_POLICY_TEMPLATE.get('rules').append(rule_policy_copy)
        priority += 1

    return copy.deepcopy(LIFECYCLE_POLICY_TEMPLATE)
