import React from 'react';

const PasswordResetPage = () => {
  // This page might have two states: one for requesting a reset, one for confirming with a token.
  // For now, a simple placeholder for the request part.
  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6">Reset Your Password</h1>

        {/* Form for requesting a password reset token/link */}
        <form>
          <p className="text-sm mb-4 text-center">
            If you've forgotten your password, enter your username or email below.
            If an account matches, instructions may be provided (offline handling).
          </p>
          <div className="mb-4">
            <label htmlFor="usernameOrEmail" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username or Email</label>
            <input type="text" id="usernameOrEmail" className="input-themed" placeholder="Enter your username or email" />
          </div>
          <button type="submit" className="btn-primary w-full mb-4">
            Request Password Reset
          </button>
        </form>

        {/* Separator or link to token confirmation form */}
        <hr className="my-6 border-wotlk-stone" />

        {/* Form for confirming password reset with a token */}
        <h2 className="text-2xl text-center mb-4">Confirm Reset</h2>
        <form>
           <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username</label>
            <input type="text" id="username" className="input-themed" placeholder="Your username" />
          </div>
          <div className="mb-4">
            <label htmlFor="resetToken" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Reset Token</label>
            <input type="text" id="resetToken" className="input-themed" placeholder="Enter the reset token you received" />
          </div>
          <div className="mb-4">
            <label htmlFor="newPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">New Password</label>
            <input type="password" id="newPassword" className="input-themed" placeholder="Enter your new password" />
          </div>
           <div className="mb-6">
            <label htmlFor="confirmNewPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Confirm New Password</label>
            <input type="password" id="confirmNewPassword" className="input-themed" placeholder="Confirm new password" />
          </div>
          <button type="submit" className="btn-primary w-full">
            Set New Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default PasswordResetPage;
