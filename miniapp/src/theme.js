import { createTheme } from '@mui/material'

const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#FF6B35', // Brand Orange
            light: '#FF8A5B',
            dark: '#E55A2B',
            contrastText: '#ffffff',
        },
        secondary: {
            main: '#2AABEE', // Brand Blue
            light: '#5AC8FA',
            dark: '#007AFF',
            contrastText: '#ffffff',
        },
        background: {
            default: '#0A2E4D', // Deep Navy
            paper: '#153B5D',   // Lighter Navy (Card bg)
            glass: 'rgba(21, 59, 93, 0.7)',
        },
        text: {
            primary: '#FFFFFF',
            secondary: '#B8CBD9',
            tertiary: '#7A92A5',
        },
        success: {
            main: '#4CAF50',
            light: '#81C784',
        },
        warning: {
            main: '#FFC107',
            light: '#FFD54F',
        },
        error: {
            main: '#F44336',
            light: '#E57373',
        },
        action: {
            hover: 'rgba(255, 255, 255, 0.08)',
            selected: 'rgba(255, 107, 53, 0.16)',
        }
    },
    typography: {
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        h1: { fontWeight: 800 },
        h2: { fontWeight: 700 },
        h3: { fontWeight: 700 },
        h4: { fontWeight: 700, letterSpacing: '-0.02em' },
        h5: { fontWeight: 700, letterSpacing: '-0.01em' },
        h6: { fontWeight: 600, letterSpacing: '0.01em' },
        subtitle1: { fontWeight: 600, color: '#B8CBD9' },
        subtitle2: { fontWeight: 500, color: '#7A92A5' },
        button: { fontWeight: 600, textTransform: 'none', letterSpacing: '0.02em' },
    },
    shape: {
        borderRadius: 16, // Softer curves
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    scrollbarWidth: 'none',
                    '&::-webkit-scrollbar': {
                        display: 'none',
                    },
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    background: 'linear-gradient(180deg, #0A2E4D 0%, rgba(10, 46, 77, 0.95) 100%)',
                    backdropFilter: 'blur(10px)',
                    boxShadow: 'none',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none', // Disable default overlay
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
                },
                rounded: {
                    borderRadius: 16,
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    padding: '10px 24px',
                    boxShadow: 'none',
                    '&:hover': {
                        boxShadow: '0 4px 12px rgba(255, 107, 53, 0.2)',
                    },
                },
                containedPrimary: {
                    background: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)',
                },
            },
        },
        MuiFab: {
            styleOverrides: {
                root: {
                    background: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)',
                    boxShadow: '0 4px 20px rgba(255, 107, 53, 0.4)',
                    '&:hover': {
                        boxShadow: '0 6px 24px rgba(255, 107, 53, 0.6)',
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    background: '#153B5D',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                },
            },
        },
        MuiTabs: {
            styleOverrides: {
                indicator: {
                    borderRadius: 3,
                    height: 3,
                    background: 'linear-gradient(90deg, #FF6B35 0%, #FF8A5B 100%)',
                },
            },
        },
        MuiTab: {
            styleOverrides: {
                root: {
                    minHeight: 64,
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#7A92A5',
                    '&.Mui-selected': {
                        color: '#FF6B35',
                    },
                },
            },
        },
        MuiDialog: {
            styleOverrides: {
                paper: {
                    background: '#153B5D',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                },
            },
        },
    },
})

export default theme
