import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from tests import TestCase, create_test_cases
from packaging import version as py_pkg_version


class AssociationTableRelationshipsTestCase(TestCase):
    def create_models(self):
        super(AssociationTableRelationshipsTestCase, self).create_models()

        class PublishedArticle(self.Model):
            __tablename__ = 'published_article'

            id = sa.Column(sa.Integer, primary_key=True)
            article_id = sa.Column(sa.Integer, sa.ForeignKey('article.id'))
            author_id = sa.Column(sa.Integer, sa.ForeignKey('author.id'))
            relationship_kwargs = {}
            if py_pkg_version.parse(sa.__version__) >= py_pkg_version.parse('1.4.0'):
                relationship_kwargs.update({'overlaps': 'articles'})
            author = relationship('Author', **relationship_kwargs)
            article = relationship('Article', **relationship_kwargs)

        self.PublishedArticle = PublishedArticle

        published_articles_table = sa.Table(PublishedArticle.__tablename__,
                                            PublishedArticle.metadata,
                                            extend_existing=True)

        class Author(self.Model):
            __tablename__ = 'author'
            __versioned__ = {
                'base_classes': (self.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            articles = relationship('Article', secondary=published_articles_table)

        self.Author = Author

    def test_version_relations(self):
        article = self.Article()
        name = u'Some article'
        article.name = name
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        assert article.versions[0].name == name

        au = self.Author(name=u'Some author')
        self.session.add(au)
        self.session.commit()
        au.articles.append(article)

        self.session.commit()


create_test_cases(AssociationTableRelationshipsTestCase)
