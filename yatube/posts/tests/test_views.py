from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from ..models import Group, Post, Follow
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import shutil
import tempfile
from time import sleep


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Group',
            slug='test-slug',
            description='Any',
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x00\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.post_list = []
        for i in range(13):
            cls.post_list.append(
                Post(
                    text='Any',
                    author=cls.user,
                    group=cls.group,
                    image=cls.uploaded
                )
            )
        Post.objects.bulk_create(cls.post_list)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_1 = Post.objects.all()[1]
        self.post_id = self.post_1.pk
        self.slug = self.group.slug

    def test_pages_uses_correct_template_guest_user(self):
        """URL matches appropriate template for guest user"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_id}): (
                        'posts/post_detail.html'),
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_id}): (
                        'users/login.html'),
            reverse('posts:post_create'): 'users/login.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_authorized_user(self):
        """URL matches appropriate template for authorized user"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_id}): (
                        'posts/post_detail.html'),
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_id}): (
                        'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Test correct context for index page"""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][1]
        post_text_5 = first_object.text
        post_author_5 = first_object.author
        post_group_5 = first_object.group
        post_image_5 = first_object.image
        self.assertEqual(post_text_5, self.post_1.text)
        self.assertEqual(post_author_5, self.post_1.author)
        self.assertEqual(post_group_5, self.post_1.group)
        self.assertEqual(post_image_5, self.post_1.image)

    def test_group_list_page_show_correct_context(self):
        """Test correct context for group list page"""
        response = self.guest_client.get(reverse('posts:group_posts',
                                                 kwargs={'slug': self.slug}))
        first_object = response.context['page_obj'][1]
        group = response.context['group']
        post_text_5 = first_object.text
        post_author_5 = first_object.author
        post_image_5 = first_object.image
        self.assertEqual(post_text_5, self.post_1.text)
        self.assertEqual(post_author_5, self.post_1.author)
        self.assertEqual(group.title, self.post_1.group.title)
        self.assertEqual(group.slug, self.post_1.group.slug)
        self.assertEqual(group.description, self.post_1.group.description)
        self.assertEqual(post_image_5, self.post_1.image)

    def test_profile_page_show_correct_context(self):
        """Test correct context for profile page"""
        author = self.user
        count_author_posts = author.posts.count()
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        first_object = response.context['page_obj'][1]
        count_posts = response.context['count_posts']
        author_context = response.context['author']
        post_image_5 = first_object.image
        self.assertEqual(first_object.text, self.post_1.text)
        self.assertEqual(first_object.group.title,
                         self.post_1.group.title)
        self.assertEqual(count_posts, count_author_posts)
        self.assertEqual(author, author_context)
        self.assertEqual(post_image_5, self.post_1.image)

    def test_post_detail_page_context(self):
        """Test correct context for post detail page"""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id}))
        object = response.context['post']
        chars_10_resp = response.context['chars_10']
        pub_date_resp = response.context['pub_date'].strftime('%Y%M%D')
        count_posts_resp = response.context['count_posts']
        author = self.user
        count_posts = author.posts.count()
        post_image_5 = object.image
        self.assertEqual(object.text, self.post_1.text)
        self.assertEqual(object.group, self.post_1.group)
        self.assertEqual(object.author, self.post_1.author)
        self.assertEqual(chars_10_resp, self.post_1.text[:10])
        self.assertEqual(
            pub_date_resp, self.post_1.pub_date.strftime('%Y%M%D'))
        self.assertEqual(count_posts_resp, count_posts)
        self.assertEqual(post_image_5, self.post_1.image)

    def test_post_create_page_context(self):
        """Test post create page form"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_context(self):
        """Test post edit page form"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        text = self.post_1.text
        group = self.post_1.group
        image = self.post_1.image
        self.assertEqual(response.context['post'].text, text)
        self.assertEqual(response.context['post'].group, group)
        self.assertEqual(response.context['post'].image, image)

    def test_first_page_contains_ten_records(self):
        """Test paginator"""
        response_index = self.client.get(reverse('posts:index'))
        response_group_posts = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.slug})
        )
        response_profile = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        quantity_list = [
            len(response_index.context['page_obj']),
            len(response_group_posts.context['page_obj']),
            len(response_profile.context['page_obj'])
        ]
        for value in quantity_list:
            with self.subTest(value=value):
                self.assertEqual(value, 10)

    def test_if_post_has_group(self):
        """Test post has group"""
        post = self.post_1
        response_index = self.guest_client.get(reverse('posts:index'))
        response_group_posts = self.guest_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.slug})
        )
        response_profile = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        object_list = [
            response_index.context['page_obj'][5].group.title,
            response_group_posts.context['page_obj'][5].group.title,
            response_profile.context['page_obj'][5].group.title,
        ]
        for value in object_list:
            with self.subTest(value=value):
                self.assertIn(post.group.title, value)

    def test_index_page_cache(self):
        """Index page cache test"""
        first_response = self.guest_client.get(reverse('posts:index'))
        Post.objects.filter(pk=1).delete()
        second_response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_response.content, second_response.content)
        sleep(21)
        third_response = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(third_response.content, second_response.content)

    def test_follow_auth(self):
        """Authorized user can follow and unfollow other users"""
        following = User.objects.create_user(username='test_author')
        first_response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': following}
            ),
            follow=True
        )
        self.assertRedirects(
            first_response,
            reverse(
                'posts:profile',
                kwargs={'username': following}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=following
            ).exists()
        )
        second_response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': following}
            ),
            follow=True
        )
        self.assertRedirects(
            second_response,
            reverse(
                'posts:profile',
                kwargs={'username': following}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=following
            ).exists()
        )

    def test_follow_index(self):
        """New user post appears in followers favorites
        and does not appear in non followers favorites
        """
        follower = User.objects.create_user(username='Follower')
        authorized_client_1 = Client()
        authorized_client_1.force_login(follower)
        not_follower = User.objects.create_user(username='Not_Follower')
        authorized_client_2 = Client()
        authorized_client_2.force_login(not_follower)
        Follow.objects.create(user=follower, author=self.user)
        response_follower = authorized_client_1.get(
            reverse(
                'posts:follow_index'
            )
        )
        response_not_follower = authorized_client_2.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertTrue(
            response_follower.context['page_obj'].object_list
        )
        self.assertFalse(
            response_not_follower.context['page_obj'].object_list
        )
