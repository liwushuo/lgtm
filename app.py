# -*- coding: utf-8 -*-

import os
from datetime import datetime

from github import Github
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from apscheduler.schedulers.tornado import TornadoScheduler
import yaml
import logging

with open('lgtm.yml') as f:
    config = yaml.load(f.read())

g = Github(config['github']['token'], base_url=config['github']['url'])
logger = logging.getLogger('lgtm')
logger.setLevel(getattr(logging, config.get('logging', {}).get('level', 'info').upper()))

def get_repos():
    return config['github']['repos']

def is_valid_comment(repo_name, pull, comment):
    if comment.body.strip().lower() not in config['github']['terms']:
        return False
    if not config['github'].get('include_self') and comment.user.login == pull.user.login:
        return False
    if comment.user.login not in config['github']['repos'][repo_name]:
        return False
    return True

def is_approved(repo_name, pull):
    comments = [
        comment for comment in pull.get_issue_comments()
        if is_valid_comment(repo_name, pull, comment)
    ]
    return len(comments) >= config['github']['approvals']


def check_repo(repo_name):
    pulls = g.get_repo(repo_name).get_pulls(state='open')

    for pull in pulls:
        if '- [ ]' in pull.body or '* [ ]' in pull.body or '+ [ ]' in pull.body:
            logger.debug('%s pull %d has incomplete tasks.', repo_name, pull.number)
            continue
        if pull.merged:
            logger.debug('%s pull %d had been merged.', repo_name, pull.number)
            continue
        if not pull.mergeable:
            logger.debug('%s pull %d is not mergeable.', repo_name, pull.number)
            continue
        if not is_approved(repo_name, pull):
            logger.debug('%s pull %d has not been approved.', repo_name, pull.number)
            continue

        pull.merge()
        logger.info('%s pull %d merged.', repo_name, pull.number)
    logger.debug('scanned %s at %s', repo_name, datetime.utcnow())

def check_repos():
    for repo_name in config['github']['repos']:
        check_repo(repo_name)

class HealthHandler(RequestHandler):
    def get(self):
        self.write("OK")

def make_app():
    return Application([
        (r"/health", HealthHandler),
    ])

if __name__ == "__main__":
    import sys
    app = make_app()
    app.listen(int(sys.argv[1]))

    scheduler = TornadoScheduler()
    scheduler.add_job(check_repos, 'interval', seconds=60)
    scheduler.start()

    try:
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        print('quit')
