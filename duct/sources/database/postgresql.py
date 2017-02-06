"""
.. module:: postgresql
   :platform: Unix
   :synopsis: A source module for postgres stats

.. moduleauthor:: Colin Alston <colin@imcol.in>
"""
from twisted.internet import defer
from twisted.enterprise import adbapi
from twisted.python import log

from zope.interface import implementer

from duct.interfaces import IDuctSource
from duct.objects import Source

from duct.aggregators import Counter64


@implementer(IDuctSource)
class PostgreSQL(Source):
    """Reads PostgreSQL metrics

    **Configuration arguments:**

    :param host: Database host
    :type host: str.
    :param port: Database port
    :type port: int.
    :param user: Username
    :type user: str.
    :param password: Password
    :type password: str.

    **Metrics:**

    :(service name).(database name).(metrics): Metrics from pg_stat_database
    """

    def __init__(self, *a, **kw):
        Source.__init__(self, *a, **kw)
        self.user = self.config.get('user', 'postgres')
        self.password = self.config.get('password', '')
        self.port = self.config.get('port', 5432)
        self.host = self.config.get('host', '127.0.0.1')

    def _get_connection(self):
        return adbapi.ConnectionPool('psycopg2',
                                      database='postgres',
                                      host=self.host,
                                      port=self.port,
                                      user=self.user,
                                      password=self.password)

    @defer.inlineCallbacks
    def get(self):
        try:
            p = self._get_connection()

            cols = (
                ('xact_commit', 'commits'),
                ('xact_rollback', 'rollbacks'),
                ('blks_read', 'disk.read'),
                ('blks_hit', 'disk.cache'),
                ('tup_returned', 'returned'),
                ('tup_fetched', 'selects'),
                ('tup_inserted', 'inserts'),
                ('tup_updated', 'updates'),
                ('tup_deleted', 'deletes'),
            )

            keys, names = zip(*cols)

            q = yield p.runQuery(
                'SELECT datname,numbackends,%s FROM pg_stat_database' % (
                    ','.join(keys))
            )

            for row in q:
                db = row[0]
                threads = row[1]
                if db not in ('template0', 'template1'):
                    self.queueBack(self.createEvent(
                        'ok',
                        'threads: %s' % threads,
                        threads,
                        prefix='%s.threads' % db
                    ))

                    for i, col in enumerate(row[2:]):
                        self.queueBack(self.createEvent(
                            'ok',
                            '%s: %s' % (names[i], col),
                            col,
                            prefix='%s.%s' % (db, names[i]),
                            aggregation=Counter64
                        ))

            yield p.close()

            defer.returnValue(self.createEvent('ok', 'Connection ok', 1,
                                               prefix='state'))

        except ImportError:
            log.msg('duct.sources.database.postgresql.PostgreSQL'
                    ' requires psycopg2')
            defer.returnValue(None)
        except Exception as e:
            defer.returnValue(self.createEvent(
                'critical',
                'Connection error: %s' % str(e).replace('\n', ' '),
                0,
                prefix='state'
            ))
