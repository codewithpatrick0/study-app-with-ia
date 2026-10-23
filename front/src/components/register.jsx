import { useState } from "react";

export function ShowRegister({ onRegistered, onGoToLogin }) {
    const [username, setUsername] = useState("");
    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    async function handleRegister(e){
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/users", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({username, full_name: fullName, email, password}),
            });

            if (response.status === 409) {
                setError("That username or email is already registered.");
                return;
            }
            if (!response.ok) {
                throw new Error("Registration failed");
            }

            onRegistered(); // Tell App the account was created
        } catch (err) {
            setError("Registration failed. Please check your data and try again.");
            console.error('error:', err)
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="auth-card">
            <h2 className="auth-title">Crea tu cuenta</h2>

            {/* Same limits as the backend schema (UserCreate), so most mistakes are caught before sending */}
            <form className="auth-form" onSubmit={handleRegister}>
                <label htmlFor="register-username">Nombre de usuario</label>
                <input
                    id="register-username"
                    type="text"
                    autoComplete="username"
                    required
                    minLength={3}
                    maxLength={50}
                    pattern="[A-Za-z0-9_.\-]+"
                    title="Letters, numbers, dots, dashes and underscores only"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <label htmlFor="register-full-name">Nombre completo</label>
                <input
                    id="register-full-name"
                    type="text"
                    autoComplete="name"
                    required
                    maxLength={150}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                />

                <label htmlFor="register-email">Correo</label>
                <input
                    id="register-email"
                    type="email"
                    autoComplete="email"
                    required
                    maxLength={255}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <label htmlFor="register-password">Contraseña</label>
                <input
                    id="register-password"
                    type="password"
                    autoComplete="new-password"
                    required
                    minLength={8}
                    maxLength={128}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit" className="primary-button" disabled={loading}>
                    {loading ? 'Registrando...' : 'Registrarse'}
                </button>
            </form>

            {error && <p className="form-error" role="alert">{error}</p>}

            <p className="auth-switch">
                ¿Ya tienes usuario?{' '}
                <button type="button" className="link-button" onClick={onGoToLogin}>
                    Inicia sesión
                </button>
            </p>
        </section>
    )
}
