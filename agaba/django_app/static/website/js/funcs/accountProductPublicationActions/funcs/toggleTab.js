export function toggleTab() {
  const state = {
    activeTabIndex: 1,
  };

  const view = {
    updateActiveTab: function() {
      const buttons = document.querySelectorAll('.sellecr__product_tab_btn');
      const tabLists = document.querySelectorAll('.seller__product_tab_list');

      buttons.forEach(button => {
        const index = button.getAttribute('data-tab-index');
        if (index == state.activeTabIndex) {
          button.classList.add('_active');
        } else {
          button.classList.remove('_active');
        }
      });

      tabLists.forEach(list => {
        const index = list.getAttribute('data-tab-index');
        if (index == state.activeTabIndex) {
          list.classList.add('_active');
        } else {
          list.classList.remove('_active');
        }
      });
    }
  };

  const controller = {
    init: function() {
      const buttons = document.querySelectorAll('.sellecr__product_tab_btn');
      buttons.forEach(button => {
        button.addEventListener('click', function() {
          const tabIndex = this.getAttribute('data-tab-index');
          controller.setActiveTab(tabIndex);
        });
      });

      view.updateActiveTab();
    },
    setActiveTab: function(index) {
      state.activeTabIndex = index;
      view.updateActiveTab();
    }
  };

  controller.init();
}
