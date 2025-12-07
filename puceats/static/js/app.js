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
})();
