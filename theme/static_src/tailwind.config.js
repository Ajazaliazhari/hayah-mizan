// const path = require('path');

// module.exports = {
//     content: [
//         // Project root templates (3 levels up from theme/static_src/)
//         path.join(__dirname, '../../../templates/**/*.html'),
//         // Any app-level templates
//         path.join(__dirname, '../../../**/templates/**/*.html'),
//         // Python files (for classes inside .py like widget attrs)
//         path.join(__dirname, '../../../**/*.py'),
//         // Theme app's own files
//         path.join(__dirname, '../templates/**/*.html'),
//     ],
//     safelist: [
//         // Dynamic classes toggled via Alpine.js :class bindings
//         'border-black',
//         'border-gray-300',
//         'border-gray-200',
//         'bg-black',
//         'text-white',
//         'bg-gray-300',
//         'text-gray-300',
//         'hover:bg-black',
//         'hover:text-white',
//         'cursor-not-allowed',
//     ],
//     theme: {
//         extend: {
//             fontFamily: {
//                 sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
//                 serif: ['"Playfair Display"', 'ui-serif', 'Georgia', 'serif'],
//             },
//             colors: {
//                 brand: {
//                     black: '#000000',
//                     white: '#ffffff',
//                 },
//             },
//         },
//     },
//     plugins: [],
// };


/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        // Paths relative to theme/static_src/
        '../../../templates/**/*.html',
        '../../../**/templates/**/*.html',
        '../../../**/*.py',
        './src/**/*.css',
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
                serif: ['"Playfair Display"', 'ui-serif', 'Georgia', 'serif'],
            },
        },
    },
    plugins: [],
};