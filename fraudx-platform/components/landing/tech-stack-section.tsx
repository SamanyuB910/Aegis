const technologies = [
  { name: "PyTorch", logo: "/pytorch-logo.png" },
  { name: "HuggingFace", logo: "/huggingface-logo.jpg" },
  { name: "Kafka", logo: "/apache-kafka-logo.jpg" },
  { name: "OpenCV", logo: "/opencv-logo.jpg" },
  { name: "Transformers", logo: "/transformers-logo.jpg" },
]

export function TechStackSection() {
  return (
    <section id="technology" className="py-24 px-4 bg-muted/30">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Powered by Industry Leaders</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Built on proven open-source technologies and enterprise-grade infrastructure
          </p>
        </div>
        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 opacity-60 hover:opacity-100 transition-opacity">
          {technologies.map((tech, index) => (
            <div key={index} className="flex items-center justify-center">
              <img
                src={tech.logo || "/placeholder.svg"}
                alt={tech.name}
                className="h-10 w-auto filter brightness-0 invert opacity-70 hover:opacity-100 transition-opacity"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
