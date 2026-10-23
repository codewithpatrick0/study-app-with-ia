import { useState } from "react";

export function ShowLogin({ onLogin, onGoToRegister, notice }) {
    const [usernameOrEmail, setUsernameOrEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);

    async function handleLogin(e){
        e.preventDefault();
        setError(null);

        try {
            const response = await fetch("http://localhost:8000/auth/login", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({username_or_email: usernameOrEmail, password}),
                credentials: 'include' // Let the browser store the auth cookie
            });

            if (!response.ok) {
                throw new Error("Login failed");
            }

            const user = await response.json();
            onLogin(user); // Tell App the login succeeded
        } catch (err) {
            setError("Login failed. Please try again.");
            console.error('error:', err)
        }
    }
    return (
        <section className="auth-card">
            <h2 className="auth-title">Inicia sesión</h2>

            {notice && <p className="form-notice" role="status">{notice}</p>}

            <form className="auth-form" onSubmit={handleLogin}>
                <label htmlFor="username-or-email">Nombre de usuario o correo</label>
                <input
                    id="username-or-email"
                    type="text"
                    autoComplete="username"
                    required
                    value={usernameOrEmail}
                    onChange={(e) => setUsernameOrEmail(e.target.value)}
                />

                <label htmlFor="password">Contraseña</label>
                <input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit" className="primary-button">Iniciar sesión</button>
            </form>

            {error && <p className="form-error" role="alert">{error}</p>}

            <p className="auth-switch">
                ¿No tienes usuario?{' '}
                <button type="button" className="link-button" onClick={onGoToRegister}>
                    Regístrate
                </button>
            </p>
        </section>
    )
}
