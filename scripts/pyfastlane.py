#!/usr/bin/env python3

import configparser
import sys
import os
import json


'''Executes and prints a command'''
def execute(cmd):
    print(cmd)
    os.system(cmd)

class App:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('app.ini')

        app = config['app']
        self.workspace = app['workspace']
        self.project = app['project']
        self.scheme = app['scheme']
        self.uses_encryption = app.get('uses encryption', False)
        self.uses_idfa = app.get('uses idfa', False)

        connect = config['connect']
        self.connect_username = connect['username']
        self.connect_team_name = connect['team_name']

        submission_information_string = json.dumps({
            'export_compliance_uses_encryption': self.uses_encryption,
            'add_id_info_uses_idfa': self.uses_idfa
        })

        self.deliver_options = f'--force --run_precheck_before_submit false --username {self.connect_username} --team_name "{self.connect_team_name}" --submission_information \'{submission_information_string}\''


    def doAction(self, action_name):
        actions = {
            'increment_build_number': self.increment_build_number,
            'build': self.build,
            'upload_binary': self.upload_binary,
            'upload_metadata': self.upload_metadata,
            'testflight': self.testflight,
            'submit': self.submit,
            'release': self.release
        }

        try:
            action = actions[action_name]
            action()
        except KeyError:
            print(f'Unknown action "{action_name}"')
            print('Available actions:')
            for action_name in actions:
                print(f'{action_name:25}: {actions[action_name].__doc__}')


    def increment_build_number(self):
        '''Increments the build number of the project'''
        execute(f'bundle exec fastlane run increment_build_number xcodeproj:"{self.project}"')


    def build(self):
        '''Builds the .ipa file'''
        execute(f'bundle exec fastlane gym --workspace {self.workspace} --scheme {self.scheme}')


    def upload_binary(self):
        '''Uploads the .ipa file to App Store Connect'''
        execute(f'bundle exec fastlane deliver {self.deliver_options} --skip_screenshots --skip_metadata')


    def upload_metadata(self):
        '''Uploads the metadata to App Store Connect'''
        execute(f'bundle exec fastlane deliver {self.deliver_options} --skip_binary_upload --skip_screenshots')


    def testflight(self):
        '''Increments build number, builds the .ipa file, then uploads the .ipa file to TestFlight'''
        self.increment_build_number()
        self.build()
        self.upload_binary()


    def submit(self):
        '''Submits the latest build for the latest version number on App Store Connect'''
        execute(f'bundle exec fastlane deliver submit_build {self.deliver_options} --skip_screenshots --skip_metadata')


    def release(self):
        '''Increments build number, builds the .ipa file, uploads the metadata and .ipa file, and submits for release on App Store Connect'''
        self.increment_build_number()
        self.build()
        execute(f'bundle exec fastlane deliver {self.deliver_options} --submit_for_review --skip_screenshots')


# Main

app = App()

for action in sys.argv[1:]:
    app.doAction(action)

