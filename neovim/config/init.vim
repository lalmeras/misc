call plug#begin()
" https://github.com/junegunn/vim-easy-align (EasyAlign)
Plug 'junegunn/vim-easy-align'
" https://github.com/junegunn/vim-github-dashboard
Plug 'junegunn/vim-github-dashboard'
" https://github.com/vim-airline/vim-airline (powerline clone)
" https://github.com/vim-airline/vim-airline-themes
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
" https://github.com/tpope/vim-fugitive (git)
Plug 'tpope/vim-fugitive'
" https://github.com/shumphrey/fugitive-gitlab.vim (fugitive + gitlab)
" Plug 'shumphrey/fugitive-gitlab.vim'
Plug 'lalmeras/fugitive-gitlab.vim', {'branch': 'dev'}
call plug#end()

" airline
" main: https://github.com/vim-airline/vim-airline
" themes: https://github.com/vim-airline/vim-airline-themes
let g:airline_theme                      = 'powerlineish'
let g:airline#extensions#tabline#enabled = 1
let g:airline_powerline_fonts            = 1
" always display laststatus
set laststatus=2

" fugitive
let g:fugitive_gitlab_domains = ['https://gitlab.openwide.fr', 'git.projects.openwide.fr']
let g:fugitive_gitlab_domains_rewrite = {
  \'git.projects.openwide.fr': 'gitlab.openwide.fr'
\}
