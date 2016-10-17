# dependencies
import pkg_resources
import json
import requests
import urllib
import hashlib

from webob.exc import HTTPFound, HTTPServerError, HTTPOk
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, String, Integer, Float, Boolean
from xblock.fragment import Fragment
from django.template import Context, Template


class QnetXBlock(XBlock):
    """
    This xblock provides external access to the qnet-plus platform
    """
    has_score = True
    always_recalculate_grades = True
    icon_class = 'other'

    # constants
    _should_be_done = True
    _secret_key = 'tortoise'

    # Settings: xblock display name
    display_name = String(
        display_name = "Display Name",
        help = "This name appears in the horizontal navigation at the top of the page.",
        scope = Scope.settings,
        default = "Qnet+ Assignment"
    )
    # Content: lab max score
    weight = Float(
        display_name = "Lab max score",
        help = "Max number of points student can get",
        scope = Scope.settings,
        default = 5.0
    )
    # Content: lab question or title
    question = String(
        display_name = "Title",
        help = "Question or subtitle for the lab.",
        scope = Scope.content,
        default = "Question?"
    )
    # Content: lab description
    description = String(
        display_name = "Description",
        help = "Description for the lab.",
        scope = Scope.content,
        default = "Description..."
    )
    # Context: used platform domain
    qnet_domain = String(
        display_name = "Platform domain",
        help = "Used platform domain.",
        scope = Scope.content,
        default = "https://qnet.bonch-ikt.ru/"
    )
    # Context: used lab path
    qnet_path = String(
        display_name = "Lab path",
        help = "Path to the platform lab (relative to domain).",
        scope = Scope.content,
        default = "stand/{element}"
    )
    # Content: used platform element
    qnet_element = String(
        display_name = "Lab element",
        help = "Used platform element for the lab.",
        scope = Scope.content,
        default = "1/1"
    )
    # Content: used lab get progress
    qnet_progress = String(
        display_name = "Lab GET progress",
        help = "Used platform api method for getting user progress (relative to domain).",
        scope = Scope.content,
        default = "api/progress?user_login={user_name}&element={element}&token={token}"
    )
    # Content: used lab get work status
    qnet_status = String(
        display_name = "Lab GET status",
        help = "Used platform api method for getting lab status (relative to domain).",
        scope = Scope.content,
        default = "api/wstatus?user_login={user_name}&element={element}&token={token}"
    )
    # Content: iteration id
    iteration_id = String(
        display_name = "Iteration ID",
        help = "Iteration ID is necessary for api requests",
        scope = Scope.content,
        default = "1/1"
    )
    # User state: score
    score = Float(
        display_name = "User score",
        help = "Number of student got points",
        scope = Scope.user_state,
        default = 0.0
    )
    # User state: is done
    is_done = Boolean(
        display_name = "User status",
        help = "Has student done the lab",
        scope = Scope.user_state,
        default = False
    )


    def load_resource(self, path):
        """Handy helper for getting resources from our kit"""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context = {}):
        """Evaluate a template by resource path, applying the provided context"""
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))


    def student_view(self, context=None):
        """
        The primary view of the QnetXBlock, shown to students
        when viewing courses.
        """
        context = {
            'title': self.display_name,
            'question': self.question,
            'description': self.description,
            'max_score': self.weight,
            'score': self.score,
            'is_done': self.is_done
        }

        html = self.render_template("static/html/student_view.html", context)

        frag = Fragment(html)
        frag.add_css(self.load_resource("static/css/qnet.css"))
        frag.add_javascript(self.load_resource("static/js/src/student_view.js"))
        frag.initialize_js('QnetXBlock')
        return frag

    def studio_view(self, context=None):
        '''
        The secondary view of the QnetXBlock, shown to teachers
        when editing the XBlock.
        '''
        context = {
            'title': self.display_name,
            'question': self.question,
            'description': self.description,
            'max_score': self.weight,
            'qnet_domain': self.qnet_domain,
            'qnet_path': self.qnet_path,
            'qnet_element': self.qnet_element,
            'qnet_progress': self.qnet_progress,
            'qnet_status': self.qnet_status,
            'iteration_id': self.iteration_id
        }

        html = self.render_template("static/html/studio_view.html", context)

        frag = Fragment(html)
        frag.add_css(self.load_resource("static/css/qnet.css"))
        frag.add_javascript(self.load_resource("static/js/src/studio_view.js"))
        frag.initialize_js('QnetXBlockEdit')
        return frag


    @XBlock.json_handler
    def save_data(self, request, suffix=''):
        """The saving handler"""
        self.display_name = request.get('title')
        self.question = request.get('question')
        self.description = request.get('description')
        self.qnet_domain = request.get('qnet_domain')
        self.qnet_path = request.get('qnet_path')
        self.qnet_progress = request.get('qnet_progress')
        self.qnet_status = request.get('qnet_status')
        self.qnet_element = request.get('qnet_element')
        self.iteration_id = request.get('iteration_id')
        self.weight = round(float(request.get('max_score')), 1)

        return {}

    @XBlock.handler
    def start_qnet_lab(self, request, suffix=''):
        """The starting handler"""
        abs_path = self.qnet_domain + self.qnet_path
        # check absolute path and used element
        if abs_path != '' and self.qnet_element != '':
            url = abs_path.format(
                element = self.qnet_element
            )
            return HTTPFound(location = url)
        else:
            return HTTPServerError(body = "Bad request to the Qnet platform")

    @XBlock.handler
    def get_qnet_progress(self, request, suffix=''):
        """The user progress checking handler"""
        abs_path = self.qnet_domain + self.qnet_progress
        # check absolute path and used element
        if abs_path != '' and self.qnet_element != '':
            # try to request
            try:
                url = self._format_api_url(abs_path)
                response = self._request_get(url)
            except Exception as e:
                return HTTPServerError(body = "GET Qnet progress error: %s" % str(e))

            # parse progress
            progress = self._convert_progress(response['progress'])
            self.is_done = progress['is_done']
            self.score = progress['score']

            # grade
            if self.is_done:
                self.runtime.publish(self, 'grade', {
                    'value': self.score,
                    'max_value': self.weight
                })

            # return result
            return HTTPOk(headers={'Content-Type': 'application/json'},
                          body=json.dumps({
                              'is_done': self.is_done,
                              'score': self.score,
                              'max_score': self.weight
                          }))

        else:
            return HTTPServerError(body = "Bad request to the Qnet platform")

    @XBlock.handler
    def get_qnet_status(self, request, suffix=''):
        """The lab status checking handler"""
        abs_path = self.qnet_domain + self.qnet_status
        # check absolute path and used element
        if abs_path != '' and self.qnet_element != '':
            # try to request
            try:
                url = self._format_api_url(abs_path)
                response = self._request_get(url)
            except Exception as e:
                return HTTPServerError(body = "GET Qnet status error: %s" % str(e))

            # return result
            return HTTPOk(headers={'Content-Type': 'application/json'},
                          body=json.dumps(response['wstatus']))

        else:
            return HTTPServerError(body="Bad request to the Qnet platform")


    def _get_user_name(self):
        """Get edx user name"""
        if self.runtime.get_real_user is None:
            return 'staff'
        else:
            return self.runtime.get_real_user(self.runtime.anonymous_student_id).username

    def _format_api_url(self, url):
        """Format used the platform api url"""
        user_name = self._get_user_name()
        # format and return url
        return url.format(
            user_name = user_name,
            element = urllib.quote(self.qnet_element.encode('utf-8'), safe=''),
            token = self._md5("%s:%s:%s" % (user_name, self.iteration_id, self._secret_key))
        )

    def _request_get(self, url):
        """Send GET request to the platform"""
        try:
            r = requests.get(url)
        except Exception:
            raise Exception('Cannot connect')
        if (r.status_code != 200):
            raise Exception('%d %s' % (r.status_code, r.text))
        if (not r.text) or (not r.text.strip()):
            raise Exception('Empty answer')
        try:
            response = json.loads(r.text)
        except Exception:
            raise Exception('Cannot parse response')
        return response

    def _convert_progress(self, progress):
        """Convert got progress to xblock score"""
        is_done = int(progress['exercises_success']) == int(progress['exercises_total'])
        score = 0.0 if (not is_done and self._should_be_done) \
            else round(self.weight * float(progress['points_reached']) / float(progress['points_total']), 1)

        return {
            'is_done': is_done,
            'score': score
        }

    @staticmethod
    def _md5(input):
        """Hash input using md5"""
        m = hashlib.md5()
        m.update(input)
        return m.hexdigest()


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("QnetXBlock",
             """<qnet/>
             """),
            ("Multiple QnetXBlock",
             """<vertical_demo>
                <qnet/>
                <qnet/>
                <qnet/>
                </vertical_demo>
             """),
        ]
