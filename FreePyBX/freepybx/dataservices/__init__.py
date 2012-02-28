"""The application's model objects"""
from freepybx.model.meta import Session, Base, User, Company, Shift, EmailAccount, PbxAccount, PbxDid, PbxProfile, PbxGateway, \
    PbxRoute, PbxEndpoint, PbxCondition, PbxGroup, PbxGroupMember, PbxAction, PbxCdr


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)

    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine, expire_on_commit=False )
    Base.query = Session.query_property()
    metadata = Base.metadata


Base.query = Session.query_property()
metadata = Base.metadata