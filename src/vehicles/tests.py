from django.test import TestCase
# import the models to test
from vehicles.models import Category, Vehicle, VehicleMake, VehicleImage
from vehicles import context_processor
from vehicles.views import get_makes_in_category


class CategoryQuerySetTest(TestCase):
    
    def setUp(self):
        self.main_category = Category.objects.create(
            category_name='Main Category',
            slug='main'
        )
        self.sub_category = Category.objects.create(
            category_parent=self.main_category,
            category_name='Sub Category',
            slug='sub'
        )
        
        self.expected_main_categories = [self.main_category]
        self.expected_sub_categories = [self.sub_category]
        tmp = [self.main_category, self.expected_sub_categories]
        self.expected_combined_categories = [tmp]
    
    def test_can_get_main_categories(self):
        actual_main_categories = Category.objects.get_main_categories()
        self.assertEquals(
            self.expected_main_categories,
            list(actual_main_categories)
        )
        
    def test_can_get_sub_categories(self):
        actual_sub_categories = Category.objects.get_sub_categories()
        self.assertEquals(
            self.expected_sub_categories,
            list(actual_sub_categories)
        )
        
    def test_can_get_sub_categories_by_category(self):
        actual_sub_categories = Category.objects.get_sub_categories_by_category(self.main_category)
        self.assertEquals(
            self.expected_sub_categories,
            list(actual_sub_categories)
        )
    
    def test_can_get_combined_categories(self):
        actual_combined_categories = Category.objects.get_categories_with_sub_categories()
        self.assertEquals(
            self.expected_combined_categories,
            actual_combined_categories
        )
    
    def test_can_get_category_by_slug(self):
        actual_category = Category.objects.get_category_by_slug('main')
        self.assertEquals(
            self.main_category,
            actual_category
        )
    
    def test_can_not_get_category_by_slug(self):
        actual_category = Category.objects.get_category_by_slug('test')
        self.assertEquals(
            None,
            actual_category
        )


class CategoryModelTest(TestCase):

    def test_str_with_category_parent(self):
        parent = 'Parent'
        child = 'Child'
        parent_category = Category.objects.create(
            category_name=parent
        )
        child_category = Category(
            category_parent=parent_category,
            category_name=child
        )

        expected_result = '{0} ({1})'.format(child, parent)

        self.assertEquals(
            str(child_category),
            expected_result
        )

    def test_str_with_no_category_parent(self):
        category_test_name = 'Test'
        category = Category(category_name=category_test_name)
        self.assertEquals(
            str(category),
            category_test_name
        )

    def test_verbose_name(self):
        self.assertEquals(
            str(Category._meta.verbose_name),
            'Category'
        )

    def test_verbose_name_plural(self):
        self.assertEquals(
            str(Category._meta.verbose_name_plural),
            'Categories'
        )


class VehicleMakeQuerySetTest(TestCase):
    
    def setUp(self):
        self.slug='toyota'
        self.make = VehicleMake.objects.create(
            v_make='Toyota',
            slug=self.slug
        )
    
    def test_can_get_make_by_slug(self):
        actual_make = VehicleMake.objects.get_make_by_slug(self.slug)
        self.assertEquals(
            self.make,
            actual_make
        )
    
    def test_can_not_get_make_by_slug(self):
        actual_make = VehicleMake.objects.get_make_by_slug('test')
        self.assertEquals(
            None,
            actual_make
        )


class VehicleMakeModelTest(TestCase):

    def test_str_representation(self):
        make_name = 'Toyota'
        vehicle_make = VehicleMake(v_make=make_name, slug=make_name.lower())
        self.assertEquals(
            str(vehicle_make),
            make_name
        )

    def test_verbose_name(self):
        self.assertEquals(
            str(VehicleMake._meta.verbose_name),
            'Make'
        )

    def test_verbose_name_plural(self):
        self.assertEquals(
            str(VehicleMake._meta.verbose_name_plural),
            'Makes'
        )


class VehicleQuerySetTest(TestCase):
    
    def setUp(self):
        # add the test makes
        self.test_make_one = VehicleMake.objects.create(
            v_make='Toyota',
            slug='toyota-test'
        )
        self.test_make_two = VehicleMake.objects.create(
            v_make='Alfa Romeo',
            slug='alfa-test'
        )
        # create a test category
        self.category = Category.objects.create(
            category_name='Main Category'
        )
        # add test vehicles
        self.vehicle = Vehicle.objects.create(
            category=self.category,
            make=self.test_make_one,
            model='Test',
            desc='Test Vehicle One'
        )
    
    def test_can_get_vehicles_by_category(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_category(self.category)
        self.assertEquals(
            [self.vehicle],
            list(actual_vehicles)
        )
    
    def test_can_not_get_vehicles_by_category(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_category(None)
        self.assertEquals(
            [], list(actual_vehicles)
        )
    
    def test_can_get_vehicles_by_category_and_make(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_category_and_make(
            self.category, self.test_make_one)
        self.assertEquals(
            [self.vehicle],
            list(actual_vehicles)
        )
    
    def test_can_not_get_vehicles_by_category_and_make(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_category_and_make(
            self.category, self.test_make_two)
        self.assertEquals(
            None,
            None
        )
    
    def test_can_get_vehicles_by_make(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_make(
            self.test_make_one
        )
        self.assertEquals(
            [self.vehicle],
            list(actual_vehicles)
        )
    
    def test_can_not_get_vehicles_by_make(self):
        actual_vehicles = Vehicle.objects.get_vehicles_by_make(
            self.test_make_two
        )
        self.assertEquals(
            None,
            None
        )


class ContextProcessorTest(TestCase):

    def test_get_all_categories_in_a_list(self):
        # setup data for test
        main_category = Category.objects.create(
            category_name='Main Category',
            slug='main-category'
        )
        sub_category = Category.objects.create(
            category_parent=main_category,
            category_name='Sub Category',
            slug='sub-category'
        )
        expected_result = [[main_category, [sub_category]]]
        # get the actual data
        categories = list(Category.objects.filter(category_parent=None))
        sub_categories = list(Category.objects.exclude(category_parent=None))
        actual_result = context_processor.get_all_categories(
            categories, sub_categories)

        self.assertEquals(
            expected_result, actual_result
        )


class CategoryDetailViewTest(TestCase):

    def setUp(self):
        # add the test makes
        self.test_make_one = VehicleMake.objects.create(
            v_make='Toyota',
            slug='toyota-test'
        )
        self.test_make_two = VehicleMake.objects.create(
            v_make='Alfa Romeo',
            slug='alfa-test'
        )
        # create a test category
        self.category = Category.objects.create(
            category_name='Main Category',
            slug='test-main-category'
        )
        # add test vehicles
        Vehicle.objects.create(
            category=self.category,
            make=self.test_make_one,
            model='Test',
            desc='Test Vehicle One'
        )
        Vehicle.objects.create(
            category=self.category,
            make=self.test_make_one,
            model='Test',
            desc='Test Vehicle Two'
        )
        Vehicle.objects.create(
            category=self.category,
            make=self.test_make_two,
            model='Test',
            desc='Test Vehicle Three'
        )

        self.makes_in_category = [self.test_make_one, self.test_make_two]

    def test_can_get_makes_in_category(self):
        actual_makes_in_category = get_makes_in_category(self.category)
        expected_makes_in_category = sorted(
            self.makes_in_category, key=lambda x: x.v_make)
        # verify both lists are equal
        self.assertEquals(
            expected_makes_in_category,
            actual_makes_in_category
        )

    def test_makes_in_category_list_is_sorted(self):
        actual_makes_in_category = get_makes_in_category(self.category)
        expected_makes_in_category = sorted(
            self.makes_in_category, key=lambda x: x.v_make, reverse=True)
        # verify both lists are not equal
        self.assertNotEquals(
            expected_makes_in_category,
            actual_makes_in_category
        )


class VehicleImageQuerySetTest(TestCase):
    
    def setUp(self):
        # add the test makes
        self.test_make_one = VehicleMake.objects.create(
            v_make='Toyota',
            slug='toyota-test'
        )
        # create a test category
        self.category = Category.objects.create(
            category_name='Main Category',
            slug='test-main-category'
        )
        # add test vehicles
        self.vehicle_with_no_images = Vehicle.objects.create(
            category=self.category,
            make=self.test_make_one,
            model='Test',
            desc='Test Vehicle One'
        )
    
    def test_can_not_get_main_image_by_vehicle(self):
        actual_image = VehicleImage.objects.get_main_image_by_vehicle(self.vehicle_with_no_images)
        self.assertEquals(
            None,
            actual_image
        )

    def test_can_not_get_images_by_vehicle_with_valid_vehicle(self):
        actual_images = VehicleImage.objects.get_images_by_vehicle(self.vehicle_with_no_images)
        self.assertEquals(
            None,
            None
        )

    def test_can_not_get_images_by_vehicle_with_invalid_vehicle(self):
        actual_images = VehicleImage.objects.get_images_by_vehicle(None)
        self.assertEquals(
            None,
            None
        )