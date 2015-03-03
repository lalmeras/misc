" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'
" sensible defaults
Plugin 'tpope/vim-sensible'
" jedi based completion
Plugin 'Valloric/YouCompleteMe'
" load .vimrc files in folder hierarchy
Plugin 'MarcWeber/vim-addon-local-vimrc'
" session and recent files management
Plugin 'mhinz/vim-startify'
" multiples colorschmes
Plugin 'flazz/vim-colorschemes'
" custom python syntax
Plugin 'hdima/python-syntax'
" python validation
Plugin 'nvie/vim-flake8'

call vundle#end()

filetype plugin indent on

" print invisible chars (tab, eol, ...)
set list
set listchars=tab:▸\ ,eol:¬,trail:·

" x11 clipboard interaction
set clipboard=unnamedplus

" smart indent
set smarttab
set tabstop=4
set shiftwidth=4

set background=dark
" python-syntax all rules
let g:python_highlight_all = 1
" colorscheme configuration
let g:solarized_termcolors=256
colorscheme solarized
