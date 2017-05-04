import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))



class Blog(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    body = db.StringProperty(required = True)



class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
    """

    def get(self):
        t = jinja_env.get_template("frontpage.html")
        content = t.render()
        self.response.write(content)

class BlogList(Handler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def get(self):
        recent_blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        t = jinja_env.get_template("bloglist.html")
        content = t.render(blogs = recent_blogs)
        self.response.write(content)

    def post(self):
        view_id = self.request.get("blog_id")
        view_post = db.GqlQuery("SELECT * FROM Blog where __key__ = KEY('Blog', {})".format(str(view_id))).get()
        t = jinja_env.get_template("view_post.html")
        content = t.render(title=view_post.title,date=str(view_post.created),body=view_post.body)
        self.response.write(content)


class Delete(Handler):

    def get(self):

        delete_id = self.request.get("deleted_blog")
        delete_blog = db.GqlQuery("SELECT * FROM Blog where __key__ = KEY('Blog', {})".format(str(delete_id))).get()

        t = jinja_env.get_template("delete.html")
        content = t.render(title=delete_blog.title,_id=delete_id)
        self.response.write(content)


    def post(self):

        delete_id = self.request.get("deleted_blog")
        delete_blog = db.GqlQuery("SELECT * FROM Blog where __key__ = KEY('Blog', {})".format(str(delete_id))).get()
        title = delete_blog.title
        delete_blog.delete()

        t = jinja_env.get_template("delete_confirm.html")
        content = t.render(title=title)
        self.response.write(content)



class NewPost(Handler):

    def get(self, title="", body="", errmsg=""):

        t = jinja_env.get_template("newpost.html")
        content = t.render(title=title,body=body,errmsg=errmsg)
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        title_escaped = cgi.escape(title, quote=True)
        body_escaped = cgi.escape(body, quote=True)
        if (title.strip() !="" and body.strip() != ""):
            blog = Blog(title=title_escaped, body=body_escaped)
            blog.put()
            t = jinja_env.get_template("post_confirm.html")
            content = t.render(title=title_escaped,body=body_escaped)
            self.response.write(content)
        else:
            errmsg="You should have a TITLE AND BODY!"
            self.get(title=title,body=body,errmsg=errmsg)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', BlogList),
    ('/newpost', NewPost),
    ('/delete', Delete)
], debug=True)
