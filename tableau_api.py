import tableauserverclient as TSC
from dotenv import load_dotenv
import git
import os
import shutil
from zipfile import ZipFile
import yaml
from pathlib import Path
import threading

class TableauApi:
    load_dotenv()
    pat_name = os.getenv('TABLEAU_PAT_NAME')
    pat_pw = os.getenv('TABLEAU_PAT_PW')
    tableau_url = os.getenv('TABLEAU_SERVER')
    site_id = os.getenv('TABLEAU_SITE')
    connection_user = os.getenv('CONNECTION_USERNAME')
    connection_pw = os.getenv('CONNECTION_PW')

    def sign_in():
        tableau_auth = TSC.PersonalAccessTokenAuth(os.getenv('TABLEAU_PAT_NAME'), os.getenv('TABLEAU_PAT_PW'), site_id= os.getenv('TABLEAU_SITE'))
        server = TSC.Server(os.getenv('TABLEAU_SERVER'), use_server_version=True)
        server.auth.sign_in(tableau_auth)
        return server

    def set_connection_credentials(connection_name, connection_password, connection_embed, connection_oauth):
        credentials = TSC.ConnectionCredentials(connection_name,connection_password,embed=connection_embed,oauth=connection_oauth)
        return credentials

    def get_file_path(input_file_name):
        for root, dirs, files in os.walk("."): 
            for filename in files:
                if filename == input_file_name:
                    filepath = os.path.join(root, filename)
                    return filepath

    def get_tableau_server_folder_id(filtered_project):
        selected_project = ''
        # get all projects on site
        all_project_items, pagination_item = TableauApi.sign_in().projects.get()
        for project in all_project_items:
                if project.name == filtered_project:
                        selected_project = project.id
        return selected_project

    def get_current_branch():
        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch
        return branch.name

    def create_domain_tableau_server_project(workbook_name, project_name):
            if TableauApi.get_tableau_server_folder_id(project_name) == '':
                domain_project = TSC.ProjectItem(name=project_name, content_permissions='LockedToProject')
                TableauApi.sign_in().projects.create(domain_project)
                certified_content = TSC.ProjectItem(name='Certified Content', content_permissions='LockedToProject', parent_id= TableauApi.get_tableau_server_folder_id(project_name))
                TableauApi.sign_in().projects.create(certified_content)

    def create_branch_tableau_server_project(parent_folder, branch_name):
        if TableauApi.get_tableau_server_folder_id(TableauApi.get_current_branch()) == '':
        # create project & project item
            branch_project = TSC.ProjectItem(name=branch_name, content_permissions='LockedToProject', parent_id=parent_folder)
            TableauApi.sign_in().projects.create(branch_project)

    def publish_tableau_server_workbook(input_tableau_workbook, input_project_id, input_connection_credentials, workbook_file_name):
        with open(TableauApi.get_file_path(workbook_file_name + '.twbx'), 'rb') as workbook_file:
            workbook_item = TSC.WorkbookItem(name = input_tableau_workbook, project_id = input_project_id, show_tabs = True)
            workbook_item = TableauApi.sign_in().workbooks.publish(workbook_item = workbook_item, file = workbook_file, mode = 'Overwrite', connection_credentials = input_connection_credentials)

    def delete_tableau_server_project(input_project_id):
        TableauApi.sign_in().projects.delete(input_project_id)

    def copy_extract_tableau_workbook(original_workbook):
        os.mkdir('./temp')
        shutil.copyfile(TableauApi.get_file_path(original_workbook + '.twbx'), './temp/' + original_workbook + '.zip')
        os.chdir('./temp/')
        with ZipFile('accounting_workbook.zip', 'r') as f:
            f.extractall()

    def replace_connection_details(environment, original_workbook):
        with open("../connection.yml", "r") as stream:
            output = yaml.safe_load(stream)
            with open(original_workbook + '.twb', 'r') as file :
                filedata = file.read()
                filedata = filedata.replace(output['connection']['server']['dev'], output['connection']['server'][environment])
                filedata = filedata.replace(output['connection']['database']['dev'], output['connection']['database'][environment])
                filedata = filedata.replace(output['connection']['schema']['dev'], output['connection']['schema'][environment])
                filedata = filedata.replace(output['connection']['username']['dev'], output['connection']['username'][environment])
                with open('./' + original_workbook + '_' + environment + '.twb', 'w') as file:
                    file.write(filedata)

    def create_twbx_file(twb_filename):
        with ZipFile('./' + twb_filename + '.twbx', 'w') as twbx_zip:
            twbx_zip.write('./' + twb_filename + '.twb', os.path.basename(twb_filename + '.twb'))

    def remove_temp_folder():
        os.chdir('../')
        shutil.rmtree('./temp')

def content_migration(workbook_name, environment):
    with open("./content.yml", "r") as stream:
        content = yaml.safe_load(stream)
        project_name = content['content'][workbook_name]['project']
        dashboard_title = content['content'][workbook_name]['title']
        workbook_filename = content['content'][workbook_name]['filename'] + '_' + environment   

        TableauApi.copy_extract_tableau_workbook(workbook_name)
        TableauApi.replace_connection_details(environment, workbook_name)
        TableauApi.create_twbx_file(workbook_name + '_' + environment)
        
        if environment == 'dev':
            TableauApi.create_branch_tableau_server_project(TableauApi.get_tableau_server_folder_id('DEV'),TableauApi.get_current_branch())
            TableauApi.publish_tableau_server_workbook(dashboard_title ,TableauApi.get_tableau_server_folder_id(TableauApi.get_current_branch()),TableauApi.set_connection_credentials(os.getenv('CONNECTION_USERNAME'),os.getenv('CONNECTION_PW'),True, False), workbook_filename)
        else :
            TableauApi.create_domain_tableau_server_project(workbook_name, project_name)
            all_projects = list(TSC.Pager(TableauApi.sign_in().projects))
            for project in all_projects:
                if project.parent_id == TableauApi.get_tableau_server_folder_id(project_name):
                    TableauApi.publish_tableau_server_workbook(dashboard_title ,project.id,TableauApi.set_connection_credentials(os.getenv('CONNECTION_USERNAME'),os.getenv('CONNECTION_PW'),True, False),workbook_filename)

        TableauApi.remove_temp_folder()

content_migration('accounting_workbook', '')