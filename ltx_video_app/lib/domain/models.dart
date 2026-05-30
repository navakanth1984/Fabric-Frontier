enum JobStatus {
  pending,
  processing,
  completed,
  failed,
  not_found;

  static JobStatus fromString(String status) {
    switch (status) {
      case 'pending':
        return JobStatus.pending;
      case 'processing':
        return JobStatus.processing;
      case 'completed':
        return JobStatus.completed;
      case 'failed':
        return JobStatus.failed;
      default:
        return JobStatus.not_found;
    }
  }
}

class GenerationJob {
  final String jobId;
  final JobStatus status;
  final String? outputUrl;
  final String? error;

  GenerationJob({
    required this.jobId,
    required this.status,
    this.outputUrl,
    this.error,
  });

  factory GenerationJob.fromJson(Map<String, dynamic> json) {
    return GenerationJob(
      jobId: json['job_id'] as String,
      status: JobStatus.fromString(json['status'] as String),
      outputUrl: json['output_url'] as String?,
      error: json['error'] as String?,
    );
  }
}
