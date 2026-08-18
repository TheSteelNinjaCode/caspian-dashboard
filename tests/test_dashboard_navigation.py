from src.components.dashboard.DashboardNavigation import DashboardNavigation


def test_navigation_renders_analytics_submenu_tree():
    result = str(DashboardNavigation())

    assert "<x-sidebar-menu-sub>" in result
    assert result.count("<x-sidebar-menu-sub-item>") == 2
    assert "Overview report" in result
    assert "Audience insights" in result
