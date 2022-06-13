import zipfile,json,shutil,platform
from pprint import pprint

from flask import Flask, render_template, jsonify, request, send_file

from project_parser import ProjectParser
from custom_lib import (
    get_request_data,
    get_stats,
    VIOLATION_MATRIX,
    WARNING_MATRIX,
    get_default_steps_to_ignore_data,
    get_flow_name_and_uuid
)
from prepareReport import Report

UPLOAD_FOLDER = 'Uploads/'
ALLOWED_EXTENSIONS = ['jar']

APP = Flask(__name__)
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

isWindows= True if platform.system() == 'Windows' else False

@APP.route("/")
def index():
    """
    Index of the website
    Return : renders index.html
    """
    context = {}
    context['default_steps_to_ignore'] = get_default_steps_to_ignore_data()
    #New step mapping added
    default_steps_mapping = get_flow_name_and_uuid()

    advance_violation_matrix = VIOLATION_MATRIX

    return render_template('index.html', context=context, steps=default_steps_mapping, rules=advance_violation_matrix)


@APP.route("/parse", methods = ['POST'])
def parse():
    """
    Parse the given OO Project
    """
    form = get_request_data(request,APP,ALLOWED_EXTENSIONS)
    proj_parser = ProjectParser(form,isWindows)
    json_result = proj_parser.process_project()   

    context = {}
    context['violations'] = VIOLATION_MATRIX
    context['warnings'] = WARNING_MATRIX
    context['title'] = proj_parser.project_name
    #context['title'] = proj_parser.file_size
    context['flows_count'] = len(json_result)
    #context['flows'] = json_result #Below it has been remodelized
    context['sys_props'] = proj_parser.sys_props_list
    context['sys_accts'] = proj_parser.sys_accts_list
    #Delete the jar file from location
    if(proj_parser.closeJARFile(True)):
        shutil.rmtree(UPLOAD_FOLDER+form['jar_file'].split('/' or '\\')[1])

    stats = get_stats(json_result)
    context['flows'] = stats['json_result']
    context['variables_count'] = len(stats['variables'])
    context['unique_variables_count'] = len(set(stats['variables']))
    context['steps_count'] = stats['steps_count']
    context['error_count'] = stats['error_count']
    context['warning_count'] = stats['warning_count']
    context['overall_variable_count'] = stats['overall_variable_count']
    

    report = Report(context)
    pdfLocation , excelLocation= report.create_Report(True)
    context['pdf_location'] = pdfLocation
    context['excel_location'] = excelLocation
    return render_template('report.html', context=context)


@APP.route("/return-files/<filename>", methods = ['GET'])
def download_excel(filename):
    filename= 'Reports/'+filename
    return send_file(filename, as_attachment=True, attachment_filename='')

@APP.route("/config")
def config():
    """
    Index of the website
    Return : renders index.html
    """
    context = {}
    context['default_steps_to_ignore'] = ""
    return render_template('update_config.html', context=context)


if __name__ == "__main__":
    #APP.run(debug=True)
    APP.run(host='0.0.0.0', port=5000,debug=True)
    #APP.run(host='0.0.0.0', port=80)
