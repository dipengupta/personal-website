from django.test import SimpleTestCase


class BasicViewTests(SimpleTestCase):
    def test_static_pages_render(self):
        pages = [
            ("/", "mysite/home.html"),
            ("/home/", "mysite/home.html"),
            ("/professional/", "mysite/sect_professional.html"),
            ("/academic/", "mysite/sect_academic.html"),
            ("/music/", "mysite/sect_music.html"),
            ("/articles/", "mysite/sect_articles.html"),
            ("/contact/", "mysite/sect_contact.html"),
            ("/explore/", "mysite/sect_travels.html"),
            ("/travels/", "mysite/sect_travels.html"),
        ]
        for path, template in pages:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_known_article_renders(self):
        for article_path in tuple(f"/articles/article{i}/" for i in range(1, 11)):
            with self.subTest(article_path=article_path):
                response = self.client.get(article_path)
                self.assertEqual(response.status_code, 200)

    def test_unknown_article_returns_404(self):
        response = self.client.get("/articles/does-not-exist/")
        self.assertEqual(response.status_code, 404)

    def test_catchall_uses_404_template_and_status(self):
        response = self.client.get("/totally-unknown-route/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "mysite/404_handler.html")
