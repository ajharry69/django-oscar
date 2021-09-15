import pytest

from oscar.navigation_menu_registry import Menu


class TestMenu:
    def test_is_placeholder(self):
        assert Menu.placeholder("id").is_placeholder is True
        assert Menu(label="").is_placeholder is False
        assert Menu(label="Not placeholder").is_placeholder is False
        assert Menu(label="", icon="Not placeholder").is_placeholder is False
        menu = Menu.placeholder("id")
        menu.label = "Makes it non-placeholder"
        assert menu.is_placeholder is False

    def test_adding_duplicate_children_merges_the_duplicates(self):
        child_d1 = Menu("D1")
        child_c1 = Menu("C1")
        child_c2 = Menu("C2")
        menu = Menu("Parent").add_child(child_d1).add_child(child_d1).add_children([child_c1, child_c1, child_c2])

        assert menu.children == [child_d1, child_c1, child_c2]
        assert len(child_d1.children) == 0
        child_d1_with_children = Menu(child_d1.label).add_child(Menu(f"Child of {child_d1.label}"))
        assert menu.add_child(child_d1_with_children).children == [child_d1_with_children, child_c1, child_c2]

    def test_adding_non_duplicate_children(self):
        menu = Menu("Catalogue", "catalogue:index")
        assert len(menu.children) == 0

        products_submenu = Menu(label="Products", url_name="catalogue:products")
        menu.add_child(products_submenu)
        assert len(menu.children) == 1

        categories_submenu = Menu(label="Categories", url_name="catalogue:categories")
        attributes_submenu = Menu(label="Attributes", url_name="catalogue:attributes")
        first_position_submenu = Menu(label="First position", url_name="catalogue:first", position=1)
        menu.add_child(categories_submenu).add_child(attributes_submenu).add_child(first_position_submenu)
        assert menu.children == [
            first_position_submenu,
            products_submenu,
            categories_submenu,
            attributes_submenu,
        ]

        first_of_first_submenu = Menu(label="FFP", url_name="catalogue:ff", position=0)
        menu.add_child(first_of_first_submenu)
        assert menu.children == [
            first_of_first_submenu,
            first_position_submenu,
            products_submenu,
            categories_submenu,
            attributes_submenu,
        ]
        copy_first_position_submenu = Menu(label="CFP", url_name="catalogue:cf", position=1)
        menu.add_child(copy_first_position_submenu)
        assert menu.children == [
            first_of_first_submenu,
            first_position_submenu,
            copy_first_position_submenu,
            products_submenu,
            categories_submenu,
            attributes_submenu,
        ]

    def test_as_navigation_dict(self):
        menu = Menu("Top level", "index")
        assert menu.as_navigation_dict() == {
            "label": "Top level",
            "url_name": "index",
            "icon": None,
            "children": [],
        }

        child_menu = Menu("Child", "child").add_child(Menu("Inner child", "inner-child"))
        menu.add_child(child_menu)
        assert menu.as_navigation_dict() == {
            "label": "Top level",
            "url_name": "index",
            "icon": None,
            "children": [
                {
                    "label": "Child",
                    "url_name": "child",
                    "icon": None,
                    "children": [
                        {
                            "label": "Inner child",
                            "url_name": "inner-child",
                            "icon": None,
                            "children": [],
                        }
                    ],
                },
            ],
        }

    def test_remove_child(self):
        parent_menu = Menu("Parent", "parent-url-name").add_child(Menu("Child", "child-url-name"))
        assert len(parent_menu.children) == 1

        parent_menu.remove_child("child")
        assert len(parent_menu.children) == 0

        with pytest.raises(ValueError):
            parent_menu.remove_child("unexisting_child")

    def test_merging_menus_with_different_identifiers_raises_exception(self):
        with pytest.raises(ValueError):
            Menu.placeholder("m1") + Menu("Menu 2", identifier="m2")

    def test_merge_menus(self):
        menu1_child = Menu.placeholder("cm1")
        menu1 = Menu.placeholder("m1").add_child(menu1_child)
        menu2 = Menu("Menu 2", identifier=menu1.identifier)

        assert (menu1 + menu2).as_navigation_dict() == {
            "label": "Menu 2",
            "url_name": None,
            "icon": None,
            "children": [
                menu1_child.as_navigation_dict(),
            ],
        }
