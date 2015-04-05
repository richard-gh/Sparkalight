# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'pet_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('profile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=230, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
        ))
        db.send_create_signal(u'pet', ['Person'])

        # Adding M2M table for field following on 'Person'
        m2m_table_name = db.shorten_name(u'pet_person_following')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_person', models.ForeignKey(orm[u'pet.person'], null=False)),
            ('to_person', models.ForeignKey(orm[u'pet.person'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_person_id', 'to_person_id'])

        # Adding model 'Board'
        db.create_table(u'pet_board', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=55)),
            ('profile', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='picture', unique=True, null=True, to=orm['pet.Picture'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('comments', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('friends', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'pet', ['Board'])

        # Adding model 'Picture'
        db.create_table(u'pet_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('board', self.gf('django.db.models.fields.related.ForeignKey')(related_name='board', to=orm['pet.Board'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'pet', ['Picture'])

        # Adding model 'BoardComment'
        db.create_table(u'pet_boardcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('board', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pet.Board'])),
        ))
        db.send_create_signal(u'pet', ['BoardComment'])

        # Adding model 'LikeBoard'
        db.create_table(u'pet_likeboard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('board', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pet.Board'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pet', ['LikeBoard'])

        # Adding model 'Friendship'
        db.create_table(u'pet_friendship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('friend', self.gf('django.db.models.fields.related.ForeignKey')(related_name='friends', to=orm['auth.User'])),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'pet', ['Friendship'])

        # Adding unique constraint on 'Friendship', fields ['user', 'friend']
        db.create_unique(u'pet_friendship', ['user_id', 'friend_id'])

        # Adding model 'Favourite'
        db.create_table(u'pet_favourite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('board', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pet.Board'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'pet', ['Favourite'])

        # Adding model 'Contact'
        db.create_table(u'pet_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Category', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'pet', ['Contact'])

        # Adding model 'IPADDRESS'
        db.create_table(u'pet_ipaddress', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100000)),
        ))
        db.send_create_signal(u'pet', ['IPADDRESS'])


    def backwards(self, orm):
        # Removing unique constraint on 'Friendship', fields ['user', 'friend']
        db.delete_unique(u'pet_friendship', ['user_id', 'friend_id'])

        # Deleting model 'Person'
        db.delete_table(u'pet_person')

        # Removing M2M table for field following on 'Person'
        db.delete_table(db.shorten_name(u'pet_person_following'))

        # Deleting model 'Board'
        db.delete_table(u'pet_board')

        # Deleting model 'Picture'
        db.delete_table(u'pet_picture')

        # Deleting model 'BoardComment'
        db.delete_table(u'pet_boardcomment')

        # Deleting model 'LikeBoard'
        db.delete_table(u'pet_likeboard')

        # Deleting model 'Friendship'
        db.delete_table(u'pet_friendship')

        # Deleting model 'Favourite'
        db.delete_table(u'pet_favourite')

        # Deleting model 'Contact'
        db.delete_table(u'pet_contact')

        # Deleting model 'IPADDRESS'
        db.delete_table(u'pet_ipaddress')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pet.board': {
            'Meta': {'object_name': 'Board'},
            'comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'friends': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '55'}),
            'picture': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'picture'", 'unique': 'True', 'null': 'True', 'to': u"orm['pet.Picture']"}),
            'profile': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.boardcomment': {
            'Meta': {'object_name': 'BoardComment'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pet.Board']"}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.contact': {
            'Category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.favourite': {
            'Meta': {'object_name': 'Favourite'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pet.Board']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.friendship': {
            'Meta': {'unique_together': "(('user', 'friend'),)", 'object_name': 'Friendship'},
            'friend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'friends'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.ipaddress': {
            'Meta': {'object_name': 'IPADDRESS'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pet.likeboard': {
            'Meta': {'object_name': 'LikeBoard'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pet.Board']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.person': {
            'Meta': {'object_name': 'Person'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '230', 'blank': 'True'}),
            'following': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'followers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['pet.Person']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'profile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pet.picture': {
            'Meta': {'object_name': 'Picture'},
            'board': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'board'", 'to': u"orm['pet.Board']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['pet']