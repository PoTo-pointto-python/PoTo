from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: aws_codebuild\nshort_description: Create or delete an AWS CodeBuild project\nnotes:\n    - For details of the parameters and returns see U(http://boto3.readthedocs.io/en/latest/reference/services/codebuild.html).\ndescription:\n    - Create or delete a CodeBuild projects on AWS, used for building code artifacts from source code.\nversion_added: "2.9"\nauthor:\n    - Stefan Horning (@stefanhorning) <horning@mediapeers.com>\nrequirements: [ botocore, boto3 ]\noptions:\n    name:\n        description:\n            - Name of the CodeBuild project.\n        required: true\n        type: str\n    description:\n        description:\n            - Descriptive text of the CodeBuild project.\n        type: str\n    source:\n        description:\n            - Configure service and location for the build input source.\n        required: true\n        suboptions:\n            type:\n                description:\n                    - "The type of the source. Allows one of these: C(CODECOMMIT), C(CODEPIPELINE), C(GITHUB), C(S3), C(BITBUCKET), C(GITHUB_ENTERPRISE)."\n                required: true\n                type: str\n            location:\n                description:\n                    - Information about the location of the source code to be built. For type CODEPIPELINE location should not be specified.\n                type: str\n            git_clone_depth:\n                description:\n                    - When using git you can specify the clone depth as an integer here.\n                type: int\n            buildspec:\n                description:\n                    - The build spec declaration to use for the builds in this build project. Leave empty if part of the code project.\n                type: str\n            insecure_ssl:\n                description:\n                    - Enable this flag to ignore SSL warnings while connecting to the project source code.\n                type: bool\n        type: dict\n    artifacts:\n        description:\n            - Information about the build output artifacts for the build project.\n        required: true\n        suboptions:\n            type:\n                description:\n                    - "The type of build output for artifacts. Can be one of the following: C(CODEPIPELINE), C(NO_ARTIFACTS), C(S3)."\n                required: true\n            location:\n                description:\n                    - Information about the build output artifact location. When choosing type S3, set the bucket name here.\n            path:\n                description:\n                    - Along with namespace_type and name, the pattern that AWS CodeBuild will use to name and store the output artifacts.\n                    - Used for path in S3 bucket when type is C(S3).\n            namespace_type:\n                description:\n                    - Along with path and name, the pattern that AWS CodeBuild will use to determine the name and location to store the output artifacts.\n                    - Accepts C(BUILD_ID) and C(NONE).\n                    - "See docs here: U(http://boto3.readthedocs.io/en/latest/reference/services/codebuild.html#CodeBuild.Client.create_project)."\n            name:\n                description:\n                    - Along with path and namespace_type, the pattern that AWS CodeBuild will use to name and store the output artifact.\n            packaging:\n                description:\n                    - The type of build output artifact to create on S3, can be NONE for creating a folder or ZIP for a ZIP file.\n        type: dict\n    cache:\n        description:\n            - Caching params to speed up following builds.\n        suboptions:\n            type:\n                description:\n                    - Cache type. Can be C(NO_CACHE) or C(S3).\n                required: true\n            location:\n                description:\n                    - Caching location on S3.\n                required: true\n        type: dict\n    environment:\n        description:\n            - Information about the build environment for the build project.\n        suboptions:\n            type:\n                description:\n                    - The type of build environment to use for the project. Usually C(LINUX_CONTAINER).\n                required: true\n            image:\n                description:\n                    - The ID of the Docker image to use for this build project.\n                required: true\n            compute_type:\n                description:\n                    - Information about the compute resources the build project will use.\n                    - "Available values include: C(BUILD_GENERAL1_SMALL), C(BUILD_GENERAL1_MEDIUM), C(BUILD_GENERAL1_LARGE)."\n                required: true\n            environment_variables:\n                description:\n                    - A set of environment variables to make available to builds for the build project. List of dictionaries with name and value fields.\n                    - "Example: { name: \'MY_ENV_VARIABLE\', value: \'test\' }"\n            privileged_mode:\n                description:\n                    - Enables running the Docker daemon inside a Docker container. Set to true only if the build project is be used to build Docker images.\n        type: dict\n    service_role:\n        description:\n            - The ARN of the AWS IAM role that enables AWS CodeBuild to interact with dependent AWS services on behalf of the AWS account.\n        type: str\n    timeout_in_minutes:\n        description:\n            - How long CodeBuild should wait until timing out any build that has not been marked as completed.\n        default: 60\n        type: int\n    encryption_key:\n        description:\n            - The AWS Key Management Service (AWS KMS) customer master key (CMK) to be used for encrypting the build output artifacts.\n        type: str\n    tags:\n        description:\n            - A set of tags for the build project.\n        type: list\n        elements: dict\n        suboptions:\n            key:\n                description: The name of the Tag.\n                type: str\n            value:\n                description: The value of the Tag.\n                type: str\n    vpc_config:\n        description:\n            - The VPC config enables AWS CodeBuild to access resources in an Amazon VPC.\n        type: dict\n    state:\n        description:\n            - Create or remove code build project.\n        default: \'present\'\n        choices: [\'present\', \'absent\']\n        type: str\nextends_documentation_fragment:\n    - aws\n    - ec2\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n- aws_codebuild:\n    name: my_project\n    description: My nice little project\n    service_role: "arn:aws:iam::123123:role/service-role/code-build-service-role"\n    source:\n        # Possible values: BITBUCKET, CODECOMMIT, CODEPIPELINE, GITHUB, S3\n        type: CODEPIPELINE\n        buildspec: \'\'\n    artifacts:\n        namespaceType: NONE\n        packaging: NONE\n        type: CODEPIPELINE\n        name: my_project\n    environment:\n        computeType: BUILD_GENERAL1_SMALL\n        privilegedMode: "true"\n        image: "aws/codebuild/docker:17.09.0"\n        type: LINUX_CONTAINER\n        environmentVariables:\n            - { name: \'PROFILE\', value: \'staging\' }\n    encryption_key: "arn:aws:kms:us-east-1:123123:alias/aws/s3"\n    region: us-east-1\n    state: present\n'
RETURN = '\nproject:\n  description: Returns the dictionary describing the code project configuration.\n  returned: success\n  type: complex\n  contains:\n    name:\n      description: Name of the CodeBuild project\n      returned: always\n      type: str\n      sample: my_project\n    arn:\n      description: ARN of the CodeBuild project\n      returned: always\n      type: str\n      sample: arn:aws:codebuild:us-east-1:123123123:project/vod-api-app-builder\n    description:\n      description: A description of the build project\n      returned: always\n      type: str\n      sample: My nice little project\n    source:\n      description: Information about the build input source code.\n      returned: always\n      type: complex\n      contains:\n        type:\n          description: The type of the repository\n          returned: always\n          type: str\n          sample: CODEPIPELINE\n        location:\n          description: Location identifier, depending on the source type.\n          returned: when configured\n          type: str\n        git_clone_depth:\n          description: The git clone depth\n          returned: when configured\n          type: int\n        build_spec:\n          description: The build spec declaration to use for the builds in this build project.\n          returned: always\n          type: str\n        auth:\n          description: Information about the authorization settings for AWS CodeBuild to access the source code to be built.\n          returned: when configured\n          type: complex\n        insecure_ssl:\n          description: True if set to ignore SSL warnings.\n          returned: when configured\n          type: bool\n    artifacts:\n      description: Information about the output of build artifacts\n      returned: always\n      type: complex\n      contains:\n        type:\n          description: The type of build artifact.\n          returned: always\n          type: str\n          sample: CODEPIPELINE\n        location:\n          description: Output location for build artifacts\n          returned: when configured\n          type: str\n        # and more... see http://boto3.readthedocs.io/en/latest/reference/services/codebuild.html#CodeBuild.Client.create_project\n    cache:\n      description: Cache settings for the build project.\n      returned: when configured\n      type: dict\n    environment:\n      description: Environment settings for the build\n      returned: always\n      type: dict\n    service_role:\n      description: IAM role to be used during build to access other AWS services.\n      returned: always\n      type: str\n      sample: arn:aws:iam::123123123:role/codebuild-service-role\n    timeout_in_minutes:\n      description: The timeout of a build in minutes\n      returned: always\n      type: int\n      sample: 60\n    tags:\n      description: Tags added to the project\n      returned: when configured\n      type: list\n    created:\n      description: Timestamp of the create time of the project\n      returned: always\n      type: str\n      sample: "2018-04-17T16:56:03.245000+02:00"\n'
from ansible.module_utils.aws.core import AnsibleAWSModule, get_boto3_client_method_parameters
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, snake_dict_to_camel_dict
try:
    import botocore
except ImportError:
    pass

def create_or_update_project(client, params, module):
    resp = {}
    name = params['name']
    formatted_params = snake_dict_to_camel_dict(dict(((k, v) for (k, v) in params.items() if v is not None)))
    permitted_create_params = get_boto3_client_method_parameters(client, 'create_project')
    permitted_update_params = get_boto3_client_method_parameters(client, 'update_project')
    formatted_create_params = dict(((k, v) for (k, v) in formatted_params.items() if k in permitted_create_params))
    formatted_update_params = dict(((k, v) for (k, v) in formatted_params.items() if k in permitted_update_params))
    found = describe_project(client=client, name=name, module=module)
    changed = False
    if 'name' in found:
        found_project = found
        resp = update_project(client=client, params=formatted_update_params, module=module)
        updated_project = resp['project']
        found_project.pop('lastModified')
        updated_project.pop('lastModified')
        if 'tags' not in updated_project:
            updated_project['tags'] = []
        if updated_project != found_project:
            changed = True
        return (resp, changed)
    try:
        resp = client.create_project(**formatted_create_params)
        changed = True
        return (resp, changed)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Unable to create CodeBuild project')

def update_project(client, params, module):
    name = params['name']
    try:
        resp = client.update_project(**params)
        return resp
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Unable to update CodeBuild project')

def delete_project(client, name, module):
    found = describe_project(client=client, name=name, module=module)
    changed = False
    if 'name' in found:
        changed = True
    try:
        resp = client.delete_project(name=name)
        return (resp, changed)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Unable to delete CodeBuild project')

def describe_project(client, name, module):
    project = {}
    try:
        projects = client.batch_get_projects(names=[name])['projects']
        if len(projects) > 0:
            project = projects[0]
        return project
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Unable to describe CodeBuild projects')

def main():
    argument_spec = dict(name=dict(required=True), description=dict(), source=dict(required=True, type='dict'), artifacts=dict(required=True, type='dict'), cache=dict(type='dict'), environment=dict(type='dict'), service_role=dict(), timeout_in_minutes=dict(type='int', default=60), encryption_key=dict(), tags=dict(type='list'), vpc_config=dict(type='dict'), state=dict(choices=['present', 'absent'], default='present'))
    module = AnsibleAWSModule(argument_spec=argument_spec)
    client_conn = module.client('codebuild')
    state = module.params.get('state')
    changed = False
    if state == 'present':
        (project_result, changed) = create_or_update_project(client=client_conn, params=module.params, module=module)
    elif state == 'absent':
        (project_result, changed) = delete_project(client=client_conn, name=module.params['name'], module=module)
    module.exit_json(changed=changed, **camel_dict_to_snake_dict(project_result))
if __name__ == '__main__':
    main()