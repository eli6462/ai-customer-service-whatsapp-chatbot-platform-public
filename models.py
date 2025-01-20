
from configs import db
from sqlalchemy.sql import func

#app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:admin#123@localhost/whatsappai"
#app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DATABASE}"


#migrate = Migrate(app, db)


class CommonDetails(db.Model):
    __abstract__ = True  # Mark this class as abstract

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Business(CommonDetails):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(80), nullable=False)
    business_whatsapp_number = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_disabled = db.Column(db.Boolean, nullable=False, default=False)
    
    credentials = db.relationship(
        "BusinessCredentials", backref="business", lazy="select", uselist=False
    )
    
    ai_assistant = db.relationship(
        "AiAssistant", backref="business", lazy="select", uselist=False
    )

    def __repr__(self):
        return '<Business %r>' % self.business_name
    
class AiAssistant(CommonDetails):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False, index=True)
    ai_assistant_id = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<AiAssistant {self.ai_assistant_id} for Business {self.business.business_name}>'

class BusinessCredentials(CommonDetails):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("business.id"))
    twilio_sid = db.Column(db.String(500), nullable=False)
    twilio_auth_token = db.Column(db.String(500), nullable=False)
    slack_bot_token = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<BusinessCredentials for {self.business.business_name}>'
    
class Client(CommonDetails):
    id = db.Column(db.Integer, primary_key=True)
    whatsapp_number = db.Column(db.String(120), unique=True, nullable=False, index=True)

    def __repr__(self):
        return '<Client %r>' % self.whatsapp_number
    
class BusinessClient(CommonDetails):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False, index=True)
    ai_thread = db.Column(db.String(500), nullable=False)
    
    business = db.relationship('Business', backref=db.backref('business_clients', lazy=True))
    client = db.relationship('Client', backref=db.backref('business_clients', lazy=True))

    def __repr__(self):
        return f'<BusinessClient {self.client.whatsapp_number} for Business {self.business.business_name}>'

class SlackUserID(CommonDetails):
    __tablename__ = 'slack_user_ids'  # Optional if you want a specific table name

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    slack_user_id = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(255), nullable=True)

    # Relationship to link back to Business
    business = db.relationship('Business', backref=db.backref('slack_user_ids', lazy=True))

    def __repr__(self):
        return f'<SlackUserID {self.slack_user_id} for Business ID {self.business_id}>'

