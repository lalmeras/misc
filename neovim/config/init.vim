call plug#begin()
" https://github.com/junegunn/vim-easy-align (EasyAlign)
Plug 'junegunn/vim-easy-align'
Plug 'junegunn/vim-github-dashboard'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
call plug#end()

" airline
" main: https://github.com/vim-airline/vim-airline
" themes: https://github.com/vim-airline/vim-airline-themes
let g:airline_theme                      = 'powerlineish'
let g:airline#extensions#tabline#enabled = 1
let g:airline_powerline_fonts            = 1
" always display laststatus
set laststatus=2

