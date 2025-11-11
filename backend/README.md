## Authentication Updates

- **Register**: Users register with `email`, `username`, and `password`.
- **Login**: Users can now login using **either their email OR username** with their password.
- **Passwords**: Are securely hashed using bcrypt (truncated to 72 bytes if necessary).
