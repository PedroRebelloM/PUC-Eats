/**
 * Sistema de Favoritos - PUC Eats
 * Gerencia favoritos usando localStorage do navegador
 */

const FavoritesManager = {
    STORAGE_KEY: 'pucEatsFavorites',

    /**
     * Obter todos os IDs de restaurantes favoritos
     * @returns {Array<number>} Array de IDs
     */
    getFavorites() {
        try {
            const favorites = localStorage.getItem(this.STORAGE_KEY);
            return favorites ? JSON.parse(favorites) : [];
        } catch (error) {
            console.error('Erro ao ler favoritos:', error);
            return [];
        }
    },

    /**
     * Salvar array de favoritos no localStorage
     * @param {Array<number>} favorites - Array de IDs
     */
    saveFavorites(favorites) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favorites));
        } catch (error) {
            console.error('Erro ao salvar favoritos:', error);
        }
    },

    /**
     * Verificar se um restaurante é favorito
     * @param {number} restaurantId - ID do restaurante
     * @returns {boolean}
     */
    isFavorite(restaurantId) {
        const favorites = this.getFavorites();
        return favorites.includes(parseInt(restaurantId));
    },

    /**
     * Adicionar restaurante aos favoritos
     * @param {number} restaurantId - ID do restaurante
     * @returns {boolean} true se adicionado com sucesso
     */
    addFavorite(restaurantId) {
        const id = parseInt(restaurantId);
        const favorites = this.getFavorites();
        
        if (!favorites.includes(id)) {
            favorites.push(id);
            this.saveFavorites(favorites);
            this.updateCounter();
            console.log(`✅ Restaurante ${id} adicionado aos favoritos`);
            return true;
        }
        
        console.log(`ℹ️ Restaurante ${id} já está nos favoritos`);
        return false;
    },

    /**
     * Remover restaurante dos favoritos
     * @param {number} restaurantId - ID do restaurante
     * @returns {boolean} true se removido com sucesso
     */
    removeFavorite(restaurantId) {
        const id = parseInt(restaurantId);
        let favorites = this.getFavorites();
        const index = favorites.indexOf(id);
        
        if (index > -1) {
            favorites.splice(index, 1);
            this.saveFavorites(favorites);
            this.updateCounter();
            console.log(`❌ Restaurante ${id} removido dos favoritos`);
            return true;
        }
        
        console.log(`ℹ️ Restaurante ${id} não está nos favoritos`);
        return false;
    },

    /**
     * Alternar favorito (adicionar se não existe, remover se existe)
     * @param {number} restaurantId - ID do restaurante
     * @returns {boolean} true se agora é favorito, false se foi removido
     */
    toggleFavorite(restaurantId) {
        if (this.isFavorite(restaurantId)) {
            this.removeFavorite(restaurantId);
            return false;
        } else {
            this.addFavorite(restaurantId);
            return true;
        }
    },

    /**
     * Obter quantidade de favoritos
     * @returns {number}
     */
    getCount() {
        return this.getFavorites().length;
    },

    /**
     * Atualizar contador visual no menu
     */
    updateCounter() {
        const count = this.getCount();
        const badge = document.querySelector('.favorites-badge');
        
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    },

    /**
     * Atualizar todos os botões de favoritar na página
     */
    updateAllButtons() {
        const buttons = document.querySelectorAll('.favorite-btn');
        
        buttons.forEach(button => {
            const restaurantId = button.getAttribute('data-restaurant-id');
            if (restaurantId) {
                this.updateButton(button, restaurantId);
            }
        });
    },

    /**
     * Atualizar estado visual de um botão específico
     * @param {HTMLElement} button - Elemento do botão
     * @param {number} restaurantId - ID do restaurante
     */
    updateButton(button, restaurantId) {
        const isFav = this.isFavorite(restaurantId);
        const icon = button.querySelector('.material-icons');
        
        if (isFav) {
            button.classList.add('active');
            if (icon) icon.textContent = 'favorite';
        } else {
            button.classList.remove('active');
            if (icon) icon.textContent = 'favorite_border';
        }
    },

    /**
     * Adicionar animação de pulso ao botão
     * @param {HTMLElement} button - Elemento do botão
     */
    animateButton(button) {
        button.classList.add('heartbeat');
        setTimeout(() => {
            button.classList.remove('heartbeat');
        }, 600);
    },

    /**
     * Limpar todos os favoritos (útil para debug)
     */
    clearAll() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.updateCounter();
        this.updateAllButtons();
        console.log('🗑️ Todos os favoritos foram removidos');
    },

    /**
     * Inicializar sistema de favoritos
     */
    init() {
        console.log('🎯 Sistema de Favoritos inicializado');
        console.log(`📊 Total de favoritos: ${this.getCount()}`);
        
        // Atualizar contador inicial
        this.updateCounter();
        
        // Atualizar todos os botões na página
        this.updateAllButtons();
        
        // Adicionar listeners aos botões de favoritar
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.favorite-btn');
            if (button) {
                const restaurantId = button.getAttribute('data-restaurant-id');
                if (restaurantId) {
                    const isFavorite = this.toggleFavorite(restaurantId);
                    this.updateButton(button, restaurantId);
                    this.animateButton(button);
                    
                    // Sincronizar outros botões do mesmo restaurante
                    this.updateAllButtons();
                    
                    // Disparar evento customizado
                    const event = new CustomEvent('favoriteChanged', {
                        detail: { restaurantId, isFavorite }
                    });
                    document.dispatchEvent(event);
                }
            }
        });
    }
};

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FavoritesManager.init());
} else {
    FavoritesManager.init();
}

// Expor globalmente para uso em outros scripts
window.FavoritesManager = FavoritesManager;
