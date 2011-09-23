""" Various tests for the Model class """

import mogo
from mogo.model import Model, InvalidUpdateCall, UnknownField
from mogo.field import ReferenceField, Field, EmptyRequiredField
import unittest


class MockCollection(object):
    pass

class Ref(Model):
    pass

class Foo(Model):

    _collection = MockCollection()

    field = Field()
    required = Field(required=True)
    default = Field(default="default")
    callback = Field(get_callback=lambda x: "foo",
                     set_callback=lambda x: "bar")
    reference = ReferenceField(Ref)
    _ignore_me = Field()


class Bar(Model):

    uid = Field(unicode)

    @classmethod
    def new(cls):
        instance = super(Bar, cls).new(uid=u"testing")
        return instance

class MogoTestModel(unittest.TestCase):

    def test_model_new_override(self):
        bar = Bar.new()
        self.assertEqual(bar.uid, "testing")

    def test_model_fields_init(self):
        """ Test that the model properly retrieves the fields """
        foo = Foo.new()
        self.assertTrue("field" in foo._fields.values())
        self.assertTrue("required" in foo._fields.values())
        self.assertTrue("callback" in foo._fields.values())
        self.assertTrue("reference" in foo._fields.values())
        self.assertTrue("default" in foo._fields.values())
        self.assertFalse("_ignore_me" in foo._fields.values())

    def test_model_create_fields_init(self):
        """ Test that the model creates fields that don't exist """
        class Testing(Model):
            pass
        try:
            mogo.AUTO_CREATE_FIELDS = True
            schemaless = Testing(foo="bar")
            self.assertEqual(schemaless["foo"], "bar")
            self.assertEqual(schemaless.foo, "bar")
            self.assertTrue("foo" in schemaless.copy())
            foo_field = getattr(Testing, "foo")
            self.assertTrue(foo_field != None)
            self.assertTrue(id(foo_field) in schemaless._fields)
        finally:
            mogo.AUTO_CREATE_FIELDS = False

    def test_model_add_field(self):
        """ Tests the ability to add a field. """
        class Testing(Model):
            pass
        Testing.add_field("foo", Field(unicode, set_callback=lambda x: u"bar"))
        self.assertTrue(isinstance(Testing.foo, Field))
        testing = Testing(foo=u"whatever")
        self.assertEqual(testing["foo"], u"bar")
        self.assertEqual(testing.foo, u"bar")
        # TODO: __setattr__ behavior

    def test_model_fail_to_create_fields_init(self):
        """ Test that model does NOT create new fields """
        class Testing(Model):
            pass
        self.assertRaises(UnknownField, Testing, foo="bar")

    def test_default_field(self):
        foo = Foo.new()
        self.assertEqual(foo["default"], "default")
        self.assertEqual(foo.default, "default")

    def test_required_fields(self):
        foo = Foo.new()
        self.assertRaises(EmptyRequiredField, foo.save)
        self.assertRaises(EmptyRequiredField, getattr, foo, "required")
        self.assertRaises(InvalidUpdateCall, foo.update, foo=u"bar")

    def test_new_constructor(self):
        foo1 = Foo.new()
        foo2 = Foo.new()
        foo1.bar = u"testing"
        foo2.bar = u"whatever"
        self.assertNotEqual(foo1.bar, foo2.bar)

    def test_null_reference(self):
        foo = Foo.new()
        foo.reference = None
        self.assertEqual(foo.reference, None)

    def test_repr(self):
        foo = Foo.new()
        foo["_id"] = 5
        self.assertEqual(str(foo), "<MogoModel:foo id:5>")