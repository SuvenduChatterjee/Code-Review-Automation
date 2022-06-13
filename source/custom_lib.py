import re,os,datetime
from werkzeug.utils import secure_filename

# variable types
INPUT_VARIABLE_TYPES = [
    'staticBinding',                # Use constant inputs
    'userInputBinding',             # Prompt inputs
    'resultBinding',                # Use Previous result inputs
    'identityBinding',              # System Account Inputs
    'loggedUserIdentityBinding',    # Logged-in user credantial input
]

# Violation Matrix
VIOLATION_MATRIX = {
    "001": "Input variable name and Assign from values are not identical",
    "002": "Hard-coded values present in use constant field",
    "003": "Input variable is using Prompt User",
    "004": "Input variable name contains sensitive keywords, but not OBFUSCATED",
    "005": "Sensitive input is assigned from USERNAME field from System Account",
    "006": "Scriptlet used in variable filter",
    "007": "try catch not implemented in Scriptlet",
    "008": "Flow Output variable created in flow steps",
    "009": "Varible is defined but not assigned",
    "010": "Description is not provided for System Property",
    "011": "Description is not provided for System Account",
    "012": "System Property is not used anywhere in this project",
}

WARNING_MATRIX = {
    "001","002","012"
}

SENSITIVE_VARIBLE_IDENTIFIERS = [
    'password',
]

def get_flow_name_and_uuid():
    """Below function gives respective uuid for each step and returns a dictionary containing uuids to skip"""
    context = {}
    context['default_steps_to_ignore'] = get_default_steps_to_ignore_data()
    file = open('./data/default_steps_to_ignore_with_name.txt', 'r')
    step_dict = {}
    for line in file:
        x=line.split(':')
        if x[0].strip() in context['default_steps_to_ignore']:
            index=x[0].strip()
            value=x[1].strip()
            step_dict[index]=value
    return step_dict

def get_key(val,my_dict): 
    """function to return key for any value""" 
    for key, value in my_dict.items():
         if val == value: 
             return key 
    return False


def allowed_file(filename,ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_request_data(request,APP,ALLOWED_EXTENSIONS):
    """
    Get the data from the request post
    """
    #jar_file = request.files['project_file']
    jar_file = request.files['project_file']

    if jar_file and allowed_file(jar_file.filename,ALLOWED_EXTENSIONS):
        filename = secure_filename(jar_file.filename)
        subFolderName = filename.split('-')[0]+ ' ' +datetime.datetime.now().strftime("%m_%d_%Y %H_%M_%S")
        os.mkdir(os.path.join(APP.config['UPLOAD_FOLDER'],subFolderName), 0o755)
        jar_file.save(os.path.join(APP.config['UPLOAD_FOLDER']+subFolderName+'/', filename))
    steps_to_ignore = request.form.get('steps_to_ignore')

    default_steps_mapping = get_flow_name_and_uuid()

    vars_to_ignore = request.form.get('vars_to_ignore')

    if steps_to_ignore:
        steps_to_ignore = steps_to_ignore.replace('\r', '').strip().split('\n')
        name_to_be_checked = []
        temp= []
        for step in steps_to_ignore:
            if get_key(step,default_steps_mapping):
                temp.append(get_key(step,default_steps_mapping))
            else:
                name_to_be_checked.append(step)
        """Keeping temp as flow names as temporary to use later if needed and steps_to_ignore is the respective
        uuid of each step name to skip specified by user if step corrosponding UUID not found the name_to_be_checked 
        will have those step names to check instead"""
        steps_to_ignore, temp = temp, steps_to_ignore
    else:
        steps_to_ignore = []
        name_to_be_checked = []

    if vars_to_ignore:
        vars_to_ignore = vars_to_ignore.replace('\r', '').strip().split('\n')
    else:
        vars_to_ignore = []

    """Last two return"""
    return {
        'jar_file': os.path.join(APP.config['UPLOAD_FOLDER']+subFolderName+'/', filename),
        'steps_to_ignore': steps_to_ignore,
        'only_errors': request.form.get("only_errors"),
        'ignore_scriptlets_in_filters': request.form.get('ignore_scriptlets_in_filters'),
        'ignore_flow_output_vars_in_steps': request.form.get("ignore_flow_output_vars_in_steps"),
        'vars_to_ignore' : vars_to_ignore,
        'save_button' : request.form.get('save_button'),
        'selected_rules' : request.form.get('selected_rules'),
        'step_names' : name_to_be_checked,
    }


def get_input_var_elements(input_element, var_type, form, opr_ref_id=None, step_name=None):
    """
    Extract input elements from given input_element
    """
    """Below two lines added"""
    user_rules= bool(form['save_button']=="True")
    user_selected_violation_rules = form['selected_rules'].split(',')

    variables = []
    sys_props = []    

    for input_var_element in input_element:
        violation = []

        variable = {
            "id": input_var_element.get('id'),
            "name": input_var_element.find('inputSymbol').text,
            "data_type": input_var_element.find('inputType').text,
            "type": var_type
        }

        assign_frm_cntxt = input_var_element.find('assignFromContext').text
        frm_cntxt_key = input_var_element.find('fromContextKey')

        if frm_cntxt_key != None and frm_cntxt_key.text != None and \
           frm_cntxt_key.text != variable['name']:
            variable['assign_from'] = frm_cntxt_key.text
            # Check if variable is assigned from system property
            if not re.match(r'.*/.+', frm_cntxt_key.text):
                if (user_rules == False or (user_rules == True and "001" in user_selected_violation_rules)):
                    violation.append("001")
            else:
                sys_props.append(frm_cntxt_key.text)

        elif assign_frm_cntxt == 'true':
            variable['assign_from'] = variable['name']

        else:
            variable['assign_from'] = "<not assigned>"
            if variable['type'] == "identityBinding":
                #violation.append("001")
                pass
            else:         
                if (user_rules == False or (user_rules == True and "009" in user_selected_violation_rules)):           
                    violation.append("009")

        # get variable default value
        value = input_var_element.find('value')
        if variable['data_type'] == "ENCRYPTED":
            variable['default_value'] = ""
        elif value is not None and value.text is not None:
            variable['default_value'] = value.text
            if (user_rules == False or (user_rules == True and "002" in user_selected_violation_rules)):
                violation.append("002")
        else:
            variable['default_value'] = ""

        for sensitive_var_identifier in SENSITIVE_VARIBLE_IDENTIFIERS:
            if sensitive_var_identifier in variable['name'].lower() \
               and variable['data_type'] != "ENCRYPTED":
               if (user_rules == False or (user_rules == True and "004" in user_selected_violation_rules)):
                    violation.append("004")
                    break

        # if variable is using system account
        if var_type == 'identityBinding':
            variable['sys_acct_uuid'] = input_var_element.\
                                        find('link/refId').text
            variable['sys_acct_ref_name'] = input_var_element.\
                                            find('link/refName').text
            variable['sys_acct_ref_attr'] = input_var_element.\
                                            find('identityAttribute').text
            variable['default_value'] = "{} : {}".format(
                                                variable['sys_acct_ref_name'],
                                                variable['sys_acct_ref_attr'])

            # Remove not assigned violation
            if "009" in violation : violation.remove("009")

            for sensitive_var_identifier in SENSITIVE_VARIBLE_IDENTIFIERS:
                if sensitive_var_identifier.lower() in \
                   variable['name'].lower() and \
                   variable['sys_acct_ref_name'] == 'USERNAME':
                   if (user_rules == False or (user_rules == True and "005" in user_selected_violation_rules)):
                        violation.append("005")

        elif var_type == "userInputBinding":
            if (user_rules == False or (user_rules == True and "003" in user_selected_violation_rules)):
                violation.append("003")

        if ((opr_ref_id and opr_ref_id in form['steps_to_ignore']) or (step_name and step_name in form['step_names'])):
            variable['violations'] = []
        elif variable['name'] in form['vars_to_ignore']:
            variable['violations'] = []
        else:
            variable['violations'] = violation

        if form['only_errors']:
            if len(variable['violations']) > 0 :
                variables.append(variable)
            else:
                continue
        else:
            variables.append(variable)

    return {
        'variables': variables,
        'sys_props': sys_props
    }


def get_stats(json_data):
    variables = []
    steps_count = 0
    error_count = 0
    warning_count = 0
    overall_variable_count = 0
    f=-1
    for flow in json_data:
        has_Warning = False
        f+=1
        steps_count += flow['steps_count']
        overall_variable_count += flow['var_count']

        iv=-1
        for inpt_var in flow['inputs']:
            iv+=1
            variables.append(inpt_var['name'])
            if len(inpt_var['violations']):
                warning_as_color = True
                for rule_no in inpt_var['violations']:
                    if rule_no in WARNING_MATRIX:
                        warning_count += 1
                        has_Warning = True
                    else:
                        error_count += 1
                        warning_as_color = False
                json_data[f]['inputs'][iv]['isWarning'] = warning_as_color

        for outpt_var in flow['outputs']:
            variables.append(outpt_var['name'])

        s=-1
        for step in flow['steps']:
            s+=1
            overall_variable_count += step['var_count']
            iv=-1
            for inpt_var in step['inputs']:
                iv+=1
                variables.append(inpt_var['name'])
                if len(inpt_var['violations']):
                    warning_as_color = True
                    for rule_no in inpt_var['violations']:
                        if rule_no in WARNING_MATRIX:
                            warning_count += 1
                            has_Warning = True
                        else:
                            error_count += 1
                            warning_as_color = False
                    json_data[f]['steps'][s]['inputs'][iv]['isWarning'] = warning_as_color
                    
            ov=-1
            for outpt_var in step['outputs']:
                ov+=1
                variables.append(outpt_var['name'])
                if len(outpt_var['violations']):
                    warning_as_color = True
                    for rule_no in outpt_var['violations']:
                        if rule_no in WARNING_MATRIX:
                            warning_count += 1
                            has_Warning = True
                        else:
                            error_count += 1
                            warning_as_color = False
                    json_data[f]['steps'][s]['outputs'][ov]['isWarning'] = warning_as_color

            json_data[f]['has_Warning'] = has_Warning  
    
    return {
        'steps_count': steps_count,
        'overall_variable_count': overall_variable_count,
        'error_count': error_count,
        'warning_count': warning_count,
        'variables': variables,
        'json_result': json_data
    }


def check_try_catch_in_js(js_script):
    """
    Validates try catch implemented in JS script
    Returns : True or False
    """
    if 'try' not in js_script or 'catch' not in js_script:
        return False
    else:
        return True


def get_default_steps_to_ignore_data():
    """
    Returns default steps ignore data
    """
    with open('./data/defaults_steps_to_ignote.txt', 'r') as file_desc:
        return file_desc.read()
