(function(){
  const body = document.body;
  const openers = document.querySelectorAll('[data-modal-target]');
  let lastFocused = null;

  function openModal(modal){
    if(!modal) return;
    lastFocused = document.activeElement;
    modal.classList.add('isOpen');
    modal.setAttribute('aria-hidden','false');
    body.classList.add('modalOpen');
  }

  function closeModal(modal){
    if(!modal) return;
    modal.classList.remove('isOpen');
    modal.setAttribute('aria-hidden','true');
    body.classList.remove('modalOpen');
    if(lastFocused && typeof lastFocused.focus === 'function'){
      try { lastFocused.focus(); } catch {}
    }
  }

  openers.forEach(opener => {
    opener.addEventListener('click', (e)=>{
      e.preventDefault();
      const targetSel = opener.getAttribute('data-modal-target');
      const modal = document.querySelector(targetSel);
      
      // Limpa o formulário quando abrir para adicionar
      const form = modal.querySelector('form');
      if (form) {
        form.reset();
        form.removeAttribute('data-dish-id');
        if (typeof updateImageChoice === 'function') updateImageChoice();
      }
      
      openModal(modal);
    });
  });

  document.addEventListener('click', (e)=>{
    const closeEl = e.target.closest('[data-modal-close]');
    if(closeEl){
      const modal = closeEl.closest('.modalContainer');
      closeModal(modal);
    }
  });

  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape'){
      const modal = document.querySelector('.modalContainer.isOpen');
      if(modal){ closeModal(modal); }
    }
  });

  const imageChoiceInputs = document.querySelectorAll('[data-image-choice]');
  const grupoUrl = document.getElementById('grupoImagemUrl');
  const grupoUpload = document.getElementById('grupoImagemUpload');
  const campoUrl = document.getElementById('campoImagemUrl');
  const campoUpload = document.getElementById('campoImagemUpload');

  function updateImageChoice(){
    const choice = document.querySelector('[data-image-choice]:checked');
    if(!choice) return;
    const val = choice.value;
    
    // Esconde tudo primeiro e remove required/disabled
    grupoUrl.classList.add('d-none');
    grupoUpload.classList.add('d-none');
    campoUrl.removeAttribute('required');
    campoUpload.removeAttribute('required');
    campoUrl.setAttribute('disabled', 'disabled');
    campoUpload.setAttribute('disabled', 'disabled');
    
    if(val === 'url'){
      grupoUrl.classList.remove('d-none');
      campoUrl.removeAttribute('disabled');
      campoUpload.value = '';
    } else if(val === 'upload'){
      grupoUpload.classList.remove('d-none');
      campoUpload.removeAttribute('disabled');
      campoUrl.value = '';
    } else {
      // nenhuma - limpa ambos e mantém desabilitados
      campoUrl.value = '';
      campoUpload.value = '';
    }
  }

  imageChoiceInputs.forEach(inp => inp.addEventListener('change', updateImageChoice));
  updateImageChoice();

  // Intercepta o envio do formulário
  const form = document.getElementById('dishForm');
  if(form){
    console.log('Formulário encontrado:', form);
    
    form.onsubmit = async function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log('Submit interceptado pelo onsubmit!');
      
      // Remove atributo required dos campos desabilitados antes de enviar
      const tipoImagemSelecionado = document.querySelector('[data-image-choice]:checked');
      if(tipoImagemSelecionado && tipoImagemSelecionado.value === 'nenhuma'){
        campoUrl.removeAttribute('required');
        campoUpload.removeAttribute('required');
        // Remove o name para que não sejam enviados
        campoUrl.removeAttribute('name');
        campoUpload.removeAttribute('name');
      }
      
      const formData = new FormData(form);
      const modal = form.closest('.modalContainer');
      
      // Se está editando, adiciona o dish_id
      const dishId = form.getAttribute('data-dish-id');
      if (dishId) {
        formData.append('dish_id', dishId);
      }
      
      // Restaura os names
      if(!campoUrl.hasAttribute('name')) campoUrl.setAttribute('name', 'imagemUrl');
      if(!campoUpload.hasAttribute('name')) campoUpload.setAttribute('name', 'imagemArquivo');
      
      try {
        const response = await fetch(form.action || window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        console.log('Response status:', response.status);
        const text = await response.text();
        console.log('Response text:', text);
        
        let result;
        try {
          result = JSON.parse(text);
        } catch (parseError) {
          console.error('JSON parse error:', parseError);
          console.error('Response was:', text);
          alert('Erro: resposta inválida do servidor');
          return;
        }
        
        if(result.success){
          // Fecha o modal
          closeModal(modal);
          
          // Limpa o formulário
          form.reset();
          form.removeAttribute('data-dish-id');
          updateImageChoice();
          
          // Recarrega a página para mostrar o novo prato
          console.log('Reloading page...');
          window.location.reload();
        } else {
          alert('Erro ao salvar: ' + (result.error || 'Erro desconhecido'));
        }
      } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao enviar o formulário: ' + error.message);
      }
      
      return false;
    };
  }

  // Filtros de busca e categoria
  const searchInput = document.getElementById('searchInput');
  const categoryFilter = document.getElementById('categoryFilter');
  const dishItems = document.querySelectorAll('.dish-item');

  function filterDishes() {
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedCategory = categoryFilter ? categoryFilter.value : '';

    dishItems.forEach(item => {
      const dishName = item.getAttribute('data-name') || '';
      const dishCategory = item.getAttribute('data-category') || '';
      
      const matchesSearch = dishName.includes(searchTerm);
      const matchesCategory = !selectedCategory || dishCategory === selectedCategory;
      
      if (matchesSearch && matchesCategory) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterDishes);
  }

  if (categoryFilter) {
    categoryFilter.addEventListener('change', filterDishes);
  }

  // Botões de deletar
  document.querySelectorAll('.btn-outline-danger[data-dish-id]').forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      const dishId = this.getAttribute('data-dish-id');
      const dishName = this.closest('.card').querySelector('.card-title').textContent;
      
      if (!confirm(`Tem certeza que deseja apagar "${dishName}"?`)) {
        return;
      }
      
      try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`/puceats/dish/${dishId}/delete/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          window.location.reload();
        } else {
          alert('Erro ao deletar: ' + (result.error || 'Erro desconhecido'));
        }
      } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao deletar o prato');
      }
    });
  });

  // Botões de editar
  document.querySelectorAll('.btnEditar[data-dish-id]').forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      const dishId = this.getAttribute('data-dish-id');
      
      try {
        const response = await fetch(`/puceats/dish/${dishId}/get/`);
        const result = await response.json();
        
        if (result.success) {
          const dish = result.dish;
          
          // Preenche o formulário
          document.getElementById('campoRestaurante').value = dish.restaurant_id;
          document.getElementById('campoNome').value = dish.name;
          document.getElementById('campoDescricao').value = dish.description;
          document.getElementById('campoCategoria').value = dish.category;
          document.getElementById('campoPreco').value = dish.price;
          
          // Armazena o ID do prato para atualizar ao invés de criar
          form.setAttribute('data-dish-id', dishId);
          
          // Abre o modal
          const modal = document.querySelector('#adicionarModal');
          openModal(modal);
        } else {
          alert('Erro ao carregar prato: ' + (result.error || 'Erro desconhecido'));
        }
      } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao carregar o prato');
      }
    });
  });
})();
