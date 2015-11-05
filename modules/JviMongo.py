import pymongo
import bson

"""
Require Pymongo 3.x +
"""

class JviMongo:
    def __init__(self, username=None, passwd=None, host='127.0.0.1', database='jvi', debug=0, log=None):
        self.debug          = debug
        self.mongo_username = username
        self.mongo_password = passwd
        self.mongo_host     = host
        self.mongo_database = database
        self.log            = log

    def mongo_connect(self):
        """ 
        create a connection to mongo database and return an object
         
        mongo URI for database connections
        mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
        """
        MongoURI = "mongodb://"

        if self.mongo_username!=None and self.mongo_password!=None: MongoURI = MongoURI + "%s:%s@" %(self.username,self.mongo_password)
        if self.mongo_host!=None: MongoURI = MongoURI + "%s" %(self.mongo_host)
        if self.mongo_database!=None: MongoURI = MongoURI + "/%s" %(self.mongo_database)

        if self.debug>0: print "JviMongo.mongo_connect: connecting to mongo using MongoURI: {%s}" %MongoURI

        try:
            mongo_client = pymongo.MongoClient(MongoURI)
            if self.debug>0: self.log.Log("JviMongo::mongo_connect: connected to database")
            return mongo_client
        except (pymongo.errors.ConnectionFailure) as e:
            self.log.Log("JviMongo::mongo_connect: %s" %e)
            return False

    def mongo_update(self, collection_name='', mongo_id="552fbc7c1ed75a072e80878e", data={}):
        if self.debug>0: print "JviMongo.mongo_update: updating mongo_id{%s} data=%s" %(mongo_id,data)
        if self.debug>0: self.log.Log("JviMongo::mongo_update: updating mongo_id{%s} data=%s" %(mongo_id, data))

        object_id  = bson.objectid.ObjectId(mongo_id)
        m_client   = self.mongo_connect()
        m_database = pymongo.database.Database(m_client, self.mongo_database)
        collection = pymongo.collection.Collection(database=m_database, name=collection_name)

        if self.debug>0:
            debugging_info = "collection information: collection.full_name=%s collection.name=%s collection.database=%s " \
                "collection(type)=%s" %(collection.full_name, collection.name, collection.database, type(collection))
            self.log.Log("JviMongo::mongo_update(): %s" %debugging_info)

        try:
            if self.debug>0:
                print "- db search info ----------->"
                for m in collection.find():
                    print m
                print "****************************\n\n"

            result = collection.update_one(
                { '_id': object_id },
                {"$set": data }
            )

            if self.debug>0:
                print "- update info --------------->"
                print "metched count: %s" %result.matched_count
                print "********************************\n\n"

            if self.debug>0:
                print "- db search info after update ->"
                for m in collection.find():
                    print m
                print "********************************\n\n"

        except (TypeError,ValueError,AttributeError) as e:
            self.log.Log("JviMongo::mongo_update: %s" %e)
            pass

    def mongo_find(self, collection_name='packages', data={}):
        try:
            m_client   = self.mongo_connect()
            m_database = pymongo.database.Database(m_client, self.mongo_database) 
            collection = pymongo.collection.Collection(database=m_database, name=collection_name)
            
            if self.debug>0: self.log.Log("JviMongo::mongo_find: collection_name{%s} data=%s" %(collection_name, data))

            return collection.find(data)
        except TypeError as e:
            self.log.Log("JviMongo::mongo_find: %s" %e)
            pass


# if __name__ == "__main__":
#     x = JviMongo(debug=1)
#     x.mongo_find(data={'building': 0})
    # x.mongo_update(collection_name='packages', mongo_id="552fbc7c1ed75a072e80878e", data={'name': 'dee dee'})