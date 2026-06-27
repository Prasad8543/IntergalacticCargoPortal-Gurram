export default function AboutUsPage() {
  return (
    <div className="card">
      <h1 className="title">About Us</h1>
      <p className="about-lead">
        The Intergalactic Cargo Portal coordinates secure manifest intake and distribution
        across deep-space logistics corridors.
      </p>
      <div className="about-grid">
        <section>
          <h2>Mission</h2>
          <p>
            Deliver accurate cargo records to authorized personnel while enforcing clearance
            levels for sensitive operations such as manifest uploads.
          </p>
        </section>
        <section>
          <h2>Access Levels</h2>
          <p>
            Admin operators manage manifests and review cargo in kilograms. Standard crew
            members receive read-only access with weights converted to pounds.
          </p>
        </section>
        <section>
          <h2>Support</h2>
          <p>
            For account or clearance issues, contact Nebula Corp operations at
            {' '}
            <a href="mailto:ops@nebula-corp.com">ops@nebula-corp.com</a>.
          </p>
        </section>
      </div>
    </div>
  );
}
