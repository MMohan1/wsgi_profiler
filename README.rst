wsgi_profiler

**wsgi_profiler** is a WSGI middleware for line-by-line profiling with mongo oprations.

wsgi_prof shows results of line-by-line profiling per request with the mongo oprations .
**wsgi_profiler UPCOMING** is a WSGI middleware for line-by-line profiling with mongo and Elastic oprations.
You can use this project with many WSGI-compatible applications and frameworks:

* Django
* Pyramid
* Flask
* Bottle
* etc...

At a Glance
-----------
You can use wsgi_profiler as a WSGI middleware of existing applications.

::

   $ git clone git@github.com:MMohan1/wsgi_profiler.git
   $ python setup.py develop

Example usage with Flask:

.. code-block:: python

   from flask import Flask, request
   from wsgi_prof.middleware import LineProfilerMiddleware
   app = Flask(__name__)


   @app.route('/')
   def index():
       time.sleep(1)
       return "Hello world!!"

   if __name__ == "__main__":
       # Add wsgi_prof as a WSGI middleware!
       app.wsgi_app =  LineProfilerMiddleware(app.wsgi_app)
       app.run(debug=True)

  
Example usage with Bottle:

.. code-block:: python

   import time

   import bottle
   from wsgi_prof.middleware import LineProfilerMiddleware

   app = bottle.default_app()


   @app.route('/')
   def index():
       time.sleep(1)
       return "Hello world!!"

   if __name__ == "__main__":
       # Add wsgi_prof as a WSGI middleware!
       app = LineProfilerMiddleware(app)
       bottle.run(app=app)

Run the above script to start web server, then access http://127.0.0.1:8080.

The results are outputted to stdout by default.
You can see the results like this:

::

   ... (snip) ...
   
   File: /Users/manmohan/projects/test/hirealchemy_ta/hirenew/modules/hire_project.py
   Name: project_status_count
   Total time: 0.651779 [sec]
   Line      Hits         Time        Mongo  Code
   ================================================
   799                                          def project_status_count(self, claims):
   800         1            1                       company_id = claims['companyId']
   801         1            1                       user_id = claims['userId']
   802         1            0                       return_data = []
   803         1            1                       query_dict = {}
   804         1            0                       if claims["is_admin"]:
   805         1       297619        Query              close_project = len(self.db_position.find({"companyId": company_id}).distinct("projectId"))\
   806         1        98614        Query                              -len(self.db_position.find({"companyId": company_id, "close": False}).distinct("projectId"))
   807         1           36                           print "\nc ****", close_project
   808         1         1389                           query_dict = {'all': {'companyId': company_id}, 'overdue': {'companyId': company_id, 'endDate__lt': arrow.now('Asia/Kolkata').datetime, },
   809         1          783                                         'ongoing': {'companyId': company_id, 'startDate__lte': arrow.now('Asia/Kolkata').datetime,
   810         1          698                                                     'endDate__gte': arrow.now('Asia/Kolkata').datetime},
   811         1          687                                         'upcoming': {'companyId': company_id, 'startDate__gt': arrow.now('Asia/Kolkata').datetime},
   812
   813                                                                }
   814                                              else:
   815                                                  auth_projects = self.prj_member.get_ids(claims['userId'])
   816                                                  query_dict = {'all': {'companyId': company_id, 'identifier__in':auth_projects.keys()},
   817                                                                'overdue': {'companyId': company_id, 'endDate__lt': arrow.now('Asia/Kolkata').datetime, 'identifier__in':auth_projects.keys()},
   818                                                                'ongoing': {'companyId': company_id, 'startDate__lte': arrow.now('Asia/Kolkata').datetime,
   819                                                                            'endDate__gte': arrow.now('Asia/Kolkata').datetime, 'identifier__in':auth_projects.keys()},
   820                                                                'upcoming': {'companyId': company_id, 'startDate__gt': arrow.now('Asia/Kolkata').datetime, 'identifier__in':auth_projects.keys()},
   821
   822                                                                }
   823                                                  close_project = len(self.db_position.find({"companyId": company_id, 'projectId': {'$in': auth_projects.keys()}}).distinct("projectId"))\
   824                                                                  -len(self.db_position.find({"companyId": company_id, "close": False, 'projectId': {'$in': auth_projects.keys()}}).distinct("projectId"))
   825                                                  # prj_to_pos_mapping = self.pos_member.get_project_position_mapping(claims['userId'])
   826                                                  # projects = Project.objects(identifier__in=auth_projects.keys()).order_by('-startDate', 'name')
   827         5            5                       for query in query_dict:
   828         4       251942        Query              return_data.append({'name': query, 'count': Project.objects(**query_dict[query]).count()})
   829         1            2                       return_data.append({'name': 'completed', 'count': close_project})
   830         1            1                       return return_data
   ... (snip) ...

Results contain many other functions, you can remove unnecessary results by
using *filters*.

Requirements
------------
* Python 2.7
* Python 3.3
* Python 3.4
* Python 3.5
* Python 3.6

Filters
-------
You can get results from specific files or sort results by using filters.
For example, use ``FilenameFilter`` to filter results with ``filename``
and use ``TotalTimeSorter`` to sort results by ``total_time``.

.. code-block:: python

    import time

    import bottle
    from wsgi_prof.filters import FilenameFilter, TotalTimeSorter
    from wsgi_prof.middleware import LineProfilerMiddleware

    app = bottle.default_app()


    def get_name():
        # Get some data...
        time.sleep(1)
        return "Monty Python"

    @app.route('/')
    def index():
        name = get_name()
        return "Hello, {}!!".format(name)

    if __name__ == "__main__":
        filters = [
            # Results which filename contains "app2.py"
            FilenameFilter("app2.py"),
            # Sort by total time of results
            TotalTimeSorter(),
        ]
        # Add wsgi_prof as a WSGI middleware
        app = LineProfilerMiddleware(app, filters=filters)

        bottle.run(app=app)

Run the above script to start web server, then access http://127.0.0.1:8080.
You can see results in stdout.

::

    $ ./app2.py
    Bottle v0.12.10 server starting up (using WSGIRefServer())...
    Listening on http://127.0.0.1:8080/
    Hit Ctrl-C to quit.

    Time unit: 1e-06 [sec]

    File: ./app2.py
    Name: index
    Total time: 1.00526 [sec]
      Line      Hits         Time  Code
    ===================================
        15                         @app.route('/')
        16                         def index():
        17         1      1005250      name = get_name()
        18         1           11      return "Hello, {}!!".format(name)

    File: ./app2.py
    Name: get_name
    Total time: 1.00523 [sec]
      Line      Hits         Time  Code
    ===================================
        10                         def get_name():
        11                             # Get some data...
        12         1      1005226      time.sleep(1)
        13         1            4      return "Monty Python"

    127.0.0.1 - - [30/Nov/2016 17:21:12] "GET / HTTP/1.1" 200 21

There are some useful filters in ``wsgi_prof.filters``.

Stream
------
By using ``stream`` option, you can output results to a file.
For example, you can output logs to ``lineprof.log``.

.. code-block:: python

    with open("lineprof.log", "w") as f:
        app = LineProfilerMiddleware(app, stream=f)
        bottle.run(app=app)

Links
-----
* `GitHub: MMohan1/wsgi_profiler <https://github.com/MMohan1/wsgi_profiler>`_

Special Thanks
^^^^^^^^^^^^^^
This project is inspired by the following projects:

* `ymyzk/wsgi_lineprof <https://github.com/ymyzk/wsgi_lineprof>`_
* `rkern/line_profiler <https://github.com/rkern/line_profiler>`_
* `kainosnoema/rack-lineprof <https://github.com/kainosnoema/rack-lineprof>`_

